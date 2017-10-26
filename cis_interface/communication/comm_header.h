#include <../tools.h>
#include <../dataio/AsciiTable.h>

/*! @brief Flag for checking if this header has already been included. */
#ifndef CISCOMMHEADER_H_
#define CISCOMMHEADER_H_

#define CIS_MSG_HEAD "CIS_MSG_HEAD"
#define HEAD_VAL_SEP ":CIS:"
#define HEAD_KEY_SEP ","
#define COMMBUFFSIZ 2000


/*! @brief Header information passed by comms for multipart messages. */
typedef struct comm_head_t {
  int size; //!< Size of incoming message.
  char address[COMMBUFFSIZ]; //!< Address that message will comm in on.
  int multipart; //!< 1 if message is multipart, 0 if it is not.
  int bodysiz; //!< Size of body.
  int bodybeg; //!< Start of body in header.
  int valid; //!< 1 if the header is valid, 0 otherwise.
  char id[COMMBUFFSIZ]; //!< Unique ID associated with this message.
  char response_address[COMMBUFFSIZ]; //!< Response address.
} comm_head_t;

/*!
  @brief Initialize a header struct.
  @param[in] size int Size of message to be sent.
  @param[in] address char* Address that should be used for remainder of 
  message following this header if it is a multipart message.
  @param[in] id char* Message ID.
  @param[in] response_address char* Address that should be used to repond to
  the message sent following this header.
  @returns comm_head_t Structure with provided information, char arrays
  correctly initialized to empty strings if NULLs provided.
 */
static inline
comm_head_t init_header(const int size, const char *address,
			const char *id, const char *response_address) {
  comm_head_t out;
  out.size = size;
  out.multipart = 0;
  out.bodysiz = 0;
  out.bodybeg = 0;
  out.valid = 1;
  if (address == NULL)
    out.address[0] = '\0';
  else
    strcpy(out.address, address);
  if (id == NULL)
    out.id[0] = '\0';
  else
    strcpy(out.id, id);
  if (response_address == NULL)
    out.response_address[0] = '\0';
  else
    strcpy(out.response_address, response_address);
  return out;
};

/*!
  @brief Format single key, value pair into header.
  @param[out] head char * Buffer where key, value pair should be written.
  @param[in] key const char * Key to be written.
  @param[in] value const char * Value to be written.
  @param[in] headsiz int Size of head buffer.
  returns: int Number of characters written.
*/
static inline
int format_header_entry(char *head, const char *key, const char *value,
			const int headsiz) {
  int ret = snprintf(head, headsiz, "%s%s%s%s",
		     key, HEAD_VAL_SEP, value, HEAD_KEY_SEP);
  if (ret > headsiz) {
    cislog_error("format_header_entry: Formatted header is larger than bufer.\n");
    return -1;
  }
  return ret;
};

/*!
  @brief Extract header value for a given key.
  @param[in] head const char * Header string.
  @param[in] key const char * Key that should be extracted.
  @param[out] value char * buffer where value should be stored.
  @param[in] valsiz int Size of value buffer.
  returns: int size of value if it could be found, -1 otherwise.
*/
static inline
int parse_header_entry(const char *head, const char *key, char *value,
		       const int valsiz) {
  int ret;
  regex_t r;
  // Compile
  if (strlen(HEAD_KEY_SEP) > 1) {
    cislog_error("parse_header_entry: HEAD_KEY_SEP is more than one character. Fix regex.");
    return -1;
  }
  char regex_text[200];
  regex_text[0] = '\0';
  strcat(regex_text, HEAD_KEY_SEP);
  strcat(regex_text, key);
  strcat(regex_text, HEAD_VAL_SEP);
  strcat(regex_text, "([^");
  strcat(regex_text, HEAD_KEY_SEP);
  strcat(regex_text, "]*)");
  strcat(regex_text, HEAD_KEY_SEP);
  ret = compile_regex(&r, regex_text);
  if (ret)
    return -1;
  // Loop until string done
  const int n_sub_matches = 10;
  regmatch_t m[n_sub_matches];
  int nomatch = regexec(&r, head, n_sub_matches, m, 0);
  if (nomatch)
    return -1;
  // Extract substring
  int value_size = m[1].rm_eo - m[1].rm_so;
  if (value_size > valsiz) {
    cislog_error("parse_header_entry: Value is larger than buffer.\n");
    return -1;
  }
  memcpy(value, head + m[1].rm_so, value_size);
  value[value_size] = '\0';
  return value_size;
};


/*!
  @brief Format header to a string.
  @param[in] head comm_head_t Header to be formatted.
  @param[out] buf char * Buffer where header should be written.
  @param[in] bufsiz int Size of buf.
  @returns: int Size of header written.
*/
static inline
int format_comm_header(const comm_head_t head, char *buf, const int bufsiz) {
  int ret, pos;
  // Header tag
  pos = 0;
  strcpy(buf, CIS_MSG_HEAD);
  pos += strlen(CIS_MSG_HEAD);
  if (pos > bufsiz) {
    cislog_error("First header tag would exceed buffer size\n");
    return -1;
  }
  // Address entry
  ret = format_header_entry(buf + pos, "address", head.address, bufsiz - pos);
  if (ret < 0) {
    cislog_error("Adding address entry would exceed buffer size\n");
    return ret;
  } else {
    pos += ret;
  }
  // Size entry
  char size_str[100];
  sprintf(size_str, "%d", head.size);
  ret = format_header_entry(buf + pos, "size", size_str, bufsiz - pos);
  if (ret < 0) {
    cislog_error("Adding size entry would exceed buffer size\n");
    return ret;
  } else {
    pos += ret;
  }
  // ID
  if (strlen(head.id) > 0) {
    ret = format_header_entry(buf + pos, "id", head.id, bufsiz - pos);
    if (ret < 0) {
      cislog_error("Adding id entry would exceed buffer size\n");
      return ret;
    } else {
      pos += ret;
    }
  }
  // RESPONSE_ADDRESS
  if (strlen(head.response_address) > 0) {
    ret = format_header_entry(buf + pos, "response_address",
			      head.response_address, bufsiz - pos);
    if (ret < 0) {
      cislog_error("Adding response_address entry would exceed buffer size\n");
      return ret;
    } else {
      pos += ret;
    }
  }
  // Closing header tag
  pos -= strlen(HEAD_KEY_SEP);
  buf[pos] = '\0';
  pos += strlen(CIS_MSG_HEAD);
  if (pos > bufsiz) {
    cislog_error("Closing header tag would exceed buffer size\n");
    return -1;
  }
  strcat(buf, CIS_MSG_HEAD);
  /* // Body */
  /* if (head.body != NULL) { */
  /*   pos += head.bodysiz; */
  /*   if (pos > bufsiz) { */
  /*     cislog_error("Adding body would exceed buffer size\n"); */
  /*     return -1; */
  /*   } */
  /*   memcpy(buf, head.body, head.bodysiz); */
  /*   buf[pos] = '\0'; */
  /* } */
  return pos;
};

/*!
  @brief Extract header information from a string.
  @param[in] buf const char* Message that header should be extracted from.
  @param[in] bufsiz int Size of buf.
  @returns: comm_head_t Header information structure.
 */
static inline
comm_head_t parse_comm_header(const char *buf, const int bufsiz) {
  comm_head_t out = init_header(0, NULL, NULL, NULL);
  // Extract just header
  char re_head[COMMBUFFSIZ] = CIS_MSG_HEAD;
  strcat(re_head, "(.*)");
  strcat(re_head, CIS_MSG_HEAD);
  strcat(re_head, "(.*)");
  int sind, eind;
  int ret = find_match(re_head, buf, &sind, &eind);
  if (ret < 0) {
    out.valid = 0;
    return out;
  } else if (ret == 0) {
    out.multipart = 0;
    /* out.size = bufsiz; */
    /* out.body = (char*)malloc(bufsiz); */
    /* memcpy(out.body, buf, bufsiz); */
  } else {
    out.multipart = 1;
    // Extract just header
    int headsiz = (eind-sind);
    out.bodysiz = bufsiz - headsiz;
    headsiz -= 2*strlen(CIS_MSG_HEAD);
    out.bodybeg = eind;
    char *head = (char*)malloc(headsiz + 2*strlen(HEAD_KEY_SEP) + 1);
    strcpy(head, HEAD_KEY_SEP);
    memcpy(head + strlen(HEAD_KEY_SEP), buf + sind + strlen(CIS_MSG_HEAD), headsiz);
    head[headsiz + strlen(HEAD_KEY_SEP)] = '\0';
    strcat(head, HEAD_KEY_SEP);
    /* out.body = (char*)malloc(out.bodysiz); */
    /* memcpy(out.body, buf + eind, out.bodysiz); */
    /* out.body[out.bodysiz] = '\0'; */
    // Extract address
    ret = parse_header_entry(head, "address", out.address, COMMBUFFSIZ);
    if (ret < 0) {
      out.valid = 0;
      free(head);
      return out;
    }
    // Extract size
    char size_str[COMMBUFFSIZ];
    ret = parse_header_entry(head, "size", size_str, COMMBUFFSIZ);
    if (ret < 0) {
      out.valid = 0;
      free(head);
      return out;
    }
    out.size = atoi(size_str);
    // Extract id & response address
    ret = parse_header_entry(head, "id", out.id, COMMBUFFSIZ);
    ret = parse_header_entry(head, "response_address", out.response_address, COMMBUFFSIZ);
    free(head);
  }
  return out;
};


#endif /*CISCOMMHEADER_H_*/
