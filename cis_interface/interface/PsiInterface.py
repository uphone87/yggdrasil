from logging import debug
import os
import time
import sysv_ipc
from cis_interface.backwards import pickle
from cis_interface.interface.scanf import scanf
from cis_interface.dataio.AsciiFile import AsciiFile
from cis_interface.dataio.AsciiTable import AsciiTable
from cis_interface import backwards, tools
from cis_interface.tools import PSI_MSG_MAX, PSI_MSG_EOF
from cis_interface.communication import DefaultComm, RPCComm


def PsiMatlab(_type, args=[]):
    r"""Short interface to identify functions called by Matlab.

    Args:
        _type (str): Name of class that should be returned.
        args (list): Additional arguments that should be passed to class
            initializer.

    Returns:
        obj: An instance of the requested class.

    """
    cls = eval(_type)
    if isinstance(cls, (int, backwards.bytes_type, backwards.unicode_type)):
        obj = cls
    else:
        kwargs = {'matlab': True}
        obj = cls(*args, **kwargs)
    return obj


class PsiInput(DefaultComm):
    r"""Class for handling input from a message queue.

    Args:
        name (str): The name of the message queue. Combined with the
            suffix '_INT', it should match an environment variable containing
            a message queue key.
        format_str (str, optional): C style format string that should be used
            to deserialize messages that are receieved into a list of python
            objects. Defaults to None and raw string messages are returned.
        
    """
    
    def __init__(self, name, format_str=None, matlab=False):
        if matlab and format_str is not None:  # pragma: matlab
            format_str = backwards.decode_escape(format_str)
        super(PsiInput, self).__init__(name, direction='recv',
                                       format_str=format_str)
        

class PsiOutput(DefaultComm):
    r"""Class for handling output to a message queue.

    Args:
        name (str): The name of the message queue. Combined with the
            suffix '_OUT', it should match an environment variable containing
            a message queue key.
        format_str (str, optional): C style format string that should be used
            to create a message from a list of python ojbects. Defaults to None
            and raw string messages are sent.
        
    """
    def __init__(self, name, format_str=None, matlab=False):
        if matlab and format_str is not None:  # pragma: matlab
            format_str = backwards.decode_escape(format_str)
        super(PsiOutput, self).__init__(name, direction='send',
                                        format_str=format_str)

    
class PsiRpc(RPCComm.RPCComm):
    r"""Class for sending a message and then receiving a response.

    Args:
        outname (str): The name of the output message queue.
        outfmt (str): Format string used to format variables in a
            message sent to the output message queue.
        inname (str): The name of the input message queue.
        infmt (str): Format string used to recover variables from
            messages received from the input message queue.

    """
    def __init__(self, outname, outfmt, inname, infmt, matlab=False):
        if matlab:  # pragma: matlab
            infmt = backwards.decode_escape(infmt)
            outfmt = backwards.decode_escape(outfmt)
        icomm_kwargs = dict(name=inname, format_str=infmt)
        ocomm_kwargs = dict(name=outname, format_str=outfmt)
        super(PsiRpc, self).__init__('%s_%s' % (inname, outname),
                                     icomm_kwargs=icomm_kwargs,
                                     ocomm_kwargs=ocomm_kwargs)

    # def rpcSend(self, *args):
    #     r"""Send arguments as a message created using the output format string.

    #     Args:
    #         \*args: All arguments are formatted using the output format string
    #             to create the message.

    #     Returns:
    #         bool: Success or failure of sending the message.

    #     """
    #     outmsg = backwards.bytes2unicode(self._outFmt) % args
    #     return self._out.send_nolimit(backwards.unicode2bytes(outmsg))

    # def rpcRecv(self):
    #     r"""Receive a message and get arguments by parsing the recieved message
    #     using the input format string.

    #     Returns:
    #         tuple (bool, tuple): Success or failure of receiving a message and
    #             the tuple of arguments retreived by parsing the message using
    #             the input format string.
        
    #     """
    #     retval, args = self._in.recv_nolimit()
    #     if retval:
    #         args = scanf(backwards.bytes2unicode(self._inFmt),
    #                      backwards.bytes2unicode(args))
    #     return retval, args

    def call(self, *args):
        r"""Send arguments using the output format string to format a message
        and then receive values back by parsing the response message with the
        input format string.

        Args:
            *args: All arguments are formatted using the output format string
                to create the message.

        Returns:
            tuple (bool, tuple): Success or failure of receiving a message and
                the tuple of arguments retreived by parsing the message using
                the input format string.
        
        """
        ret = self.send_nolimit(*args)
        if ret:
            return self.recv_nolimit(timeout=False)


class PsiRpcServer(PsiRpc):
    r"""Class for handling requests and response for an RPC Server.

    Args:
        name (str): The name of the server queues.
        infmt (str): Format string used to recover variables from
            messages received from the request queue.
        outfmt (str): Format string used to format variables in a
            message sent to the response queue.

    """
    def __init__(self, name, infmt, outfmt, matlab=False):
        super(PsiRpcServer, self).__init__(name, outfmt, name, infmt)
    

class PsiRpcClient(PsiRpc):
    r"""Class for handling requests and response to an RPC Server from a
    client.

    Args:
        name (str): The name of the server queues.
        outfmt (str): Format string used to format variables in a
            message sent to the request queue.
        infmt (str): Format string used to recover variables from
            messages received from the response queue.

    """
    def __init__(self, name, outfmt, infmt, matlab=False):
        super(PsiRpcClient, self).__init__(name, outfmt, name, infmt)
    

# Specialized classes for ascii IO
class PsiAsciiFileInput(object):
    r"""Class for generic ASCII input from either a file or message queue.

    Args:
        name (str): Path to the local file that input should be read from (if
            src_type == 0) or the name of the input message queue that input
            should be received from.
        src_type (int, optional): If 0, input is read from a local file.
            Otherwise input is received from a message queue. Defauts to 1.

    """
    _name = None
    _type = 0
    _file = None
    _psi = None

    def __init__(self, name, src_type=1, matlab=False):
        self._name = name
        self._type = src_type
        if self._type == 0:
            self._file = AsciiFile(name, 'r')
            self._file.open()
        else:
            self._psi = PsiInput(name)
            self._file = AsciiFile(name, None)

    def __del__(self):
        if self._type == 0 and (self._file is not None):
            self._file.close()
            self._file = None

    def recv_line(self):
        r"""Receive a single line of ASCII input.

        Returns:
            tuple(bool, str): Success or failure of receiving a line and the
                line received (including the newline character).

        """
        if self._type == 0:
            eof, line = self._file.readline()
            ret = (not eof)
        else:
            ret, line = self._psi.recv()
            if (len(line) == 0) or (line == PSI_MSG_EOF):
                ret = False
        return ret, line


class PsiAsciiFileOutput(object):
    r"""Class for generic ASCII output to either a local file or message
    queue.

    Args:
        name (str): Path to the local file where output should be written (if
            dst_type == 0) or the name of the message queue where output should
            be sent.
        dst_type (int, optional): If 0, output is written to a local file.
            Otherwise, output is sent to a message queue. Defaults to 1.

    """
    _name = None
    _type = 0
    _file = None
    _psi = None

    def __init__(self, name, dst_type=1, matlab=False):
        self._name = name
        self._type = dst_type
        if self._type == 0:
            self._file = AsciiFile(name, 'w')
            self._file.open()
        else:
            self._psi = PsiOutput(name)
            self._file = AsciiFile(name, None)

    def __del__(self):
        if self._type == 0 and (self._file is not None):
            self._file.close()
            self._file = None

    def send_eof(self):
        r"""Send an end-of-file message to the message queue."""
        if self._type == 0:
            pass
        else:
            self._psi.send(PSI_MSG_EOF)

    def send_line(self, line):
        r"""Output a single ASCII line.

        Args:
            line (str): Line to output (including newline character).

        Returns:
            bool: Success or failure of sending the line.

        """
        if self._type == 0:
            self._file.writeline(line)
            ret = True
        else:
            ret = self._psi.send(line)
        return ret


# Specialized classes for ascii table IO
class PsiAsciiTableInput(object):
    r"""Class for handling table-like formatted input.

    Args:
        name (str): The path to the local file to read input from (if src_type
            == 0) or the name of the message queue input should be received
            from.
        src_type (int, optional): If 0, input is read from a local file.
            Otherwise, the input is received from a message queue. Defaults to
            1.

    """
    _name = None
    _type = 0
    _table = None
    _psi = None

    def __init__(self, name, src_type=1, matlab=False):
        self._name = name
        self._type = src_type
        if self._type == 0:
            self._table = AsciiTable(name, 'r')
            self._table.open()
        else:
            self._psi = PsiInput(name)
            ret, format_str = self._psi.recv()
            if not ret:  # pragma: debug
                raise Exception('PsiAsciiTableInput could not receive format' +
                                'string from input.')
            self._table = AsciiTable(
                name, None, format_str=backwards.decode_escape(format_str))

    def __del__(self):
        if self._type == 0:
            self._table.close()

    def recv_row(self):
        r"""Receive a single row of variables from the input.

        Returns:
            tuple(bool, tuple): Success or failure of receiving the row and
                the variables recovered from the row.

        """
        if self._type == 0:
            eof, args = self._table.readline()
            ret = (not eof)
        else:
            ret, args = self._psi.recv_nolimit()
            if ret:
                args = self._table.process_line(args)
                if args is None:
                    ret = False
        return ret, args

    def recv_array(self):
        r"""Receive an entire array of table data.

        Returns:
            tuple(bool, np.ndarray): Success or failure of receiving the row
                and the array of table data.

        """
        if self._type == 0:
            arr = self._table.read_array()
            ret = True
        else:
            ret, data = self._psi.recv_nolimit()
            if ret:
                arr = self._table.bytes_to_array(data, order='F')
                if arr is None:  # pragma: debug
                    ret = False
            else:  # pragma: debug
                arr = None
        return ret, arr


class PsiAsciiTableOutput(object):
    r"""Class for handling table-like formatted output.

    Args:
        name (str): The path to the local file where output should be saved
            (if dst_type == 0) or the name of the message queue where the
            output should be sent.
        fmt (str): A C style format string specifying how each 'row' of output
            should be formated. This should include the newline character.
        dst_type (int, optional): If 0, output is sent to a local file.
            Otherwise, the output is sent to a message queue. Defaults to 1.

    """
    _name = None
    _type = 0
    _table = None
    _psi = None

    def __init__(self, name, fmt, dst_type=1, matlab=False):
        self._name = name
        self._type = dst_type
        if matlab:  # pragma: matlab
            fmt = backwards.decode_escape(fmt)
        if self._type == 0:
            self._table = AsciiTable(name, 'w', format_str=fmt)
            self._table.open()
            self._table.writeformat()
        else:
            self._psi = PsiOutput(name)
            self._table = AsciiTable(name, None, format_str=fmt)
            self._psi.send(backwards.decode_escape(fmt))

    def __del__(self):
        if self._type == 0:
            self._table.close()

    def send_eof(self):
        r"""Send an end-of-file message to the message queue."""
        if self._type == 0:
            self._table.close()
        else:
            self._psi.send_nolimit(PSI_MSG_EOF)

    def send_row(self, *args):
        r"""Output arguments as a formated row to either a local file or
        message queue.

        Args:
            \*args: All arguments are formated to create a table 'row'.

        Returns:
            bool: Success or failure of outputing the row.

        """
        if (len(args) == 1) and isinstance(args[0], tuple):
            args = args[0]
        if self._type == 0:
            self._table.writeline(*args)
            ret = True
        else:
            msg = self._table.format_line(*args)
            ret = self._psi.send_nolimit(msg)
        return ret

    def send_array(self, arr):
        r"""Output an array of table data to either a local file or message
        sueue.

        Args:
            arr (numpy.ndarray): Array of table data. The first dimension is
                assumed to be table rows and the second dimension is assumed to
                be table columns.

        Returns:
            bool: Success or failure of outputing the array.

        """
        if self._type == 0:
            self._table.write_array(arr, append=True)
            ret = True
        else:
            msg = self._table.array_to_bytes(arr, order='F')
            ret = self._psi.send_nolimit(msg)
        return ret

    
class PsiPickleInput(object):
    r"""Class for handling pickled input.

    Args:
        name (str): The path to the local file to read input from (if src_type
            == 0) or the name of the message queue input should be received
            from.
        src_type (int, optional): If 0, input is read from a local file.
            Otherwise, the input is received from a message queue. Defaults to
            1.

    """
    _name = None
    _type = 1
    _file = None
    _psi = None

    def __init__(self, name, src_type=1, matlab=False):
        self._name = name
        self._type = src_type
        if self._type == 0:
            self._file = open(name, 'rb')
        else:
            self._psi = PsiInput(name)

    def __del__(self):
        if self._type == 0 and (self._file is not None):
            self._file.close()
            self._file = None

    def recv(self):
        r"""Receive a single pickled object.

        Returns:
            tuple(bool, object): Success or failure of receiving a pickled
                object and the unpickled object that was received.

        """
        if self._type == 0:
            try:
                obj = pickle.load(self._file)
                eof = False
            except EOFError:  # pragma: debug
                obj = None
                eof = True
            ret = (not eof)
        else:
            ret, obj = self._psi.recv_nolimit()
            try:
                obj = pickle.loads(obj)
            except pickle.UnpicklingError:  # pragma: debug
                obj = None
                ret = False
        return ret, obj


class PsiPickleOutput(object):
    r"""Class for handling pickled output.

    Args:
        name (str): The path to the local file where output should be saved
            (if dst_type == 0) or the name of the message queue where the
            output should be sent.
        fmt (str): A C style format string specifying how each 'row' of output
            should be formated. This should include the newline character.
        dst_type (int, optional): If 0, output is sent to a local file.
            Otherwise, the output is sent to a message queue. Defaults to 1.

    """
    _name = None
    _type = 0
    _file = None
    _psi = None

    def __init__(self, name, dst_type=1, matlab=False):
        self._name = name
        self._type = dst_type
        if self._type == 0:
            self._file = open(name, 'wb')
        else:
            self._psi = PsiOutput(name)

    def __del__(self):
        if self._type == 0 and (self._file is not None):
            self._file.close()
            self._file = None

    def send(self, obj):
        r"""Output an object as a pickled string to either a local file or
        message queue.

        Args:
            obj (object): Any python object that can be pickled.

        Returns:
            bool: Success or failure of outputing the pickled object.

        """
        if self._type == 0:
            try:
                pickle.dump(obj, self._file)
                ret = True
            except pickle.PicklingError:  # pragma: debug
                ret = False
        else:
            try:
                msg = pickle.dumps(obj)
                ret = True
            except pickle.PicklingError:  # pragma: debug
                ret = False
            if ret:
                ret = self._psi.send_nolimit(msg)
        return ret
