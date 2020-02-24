#include "c_wrappers.h"

// Utilities
void ygg_c_free(void *x) {
  if (x != NULL) {
    free(x);
  }
}

void ygg_log_info_f(const char* fmt) {
  ygglog_info(fmt);
}
void ygg_log_debug_f(const char* fmt) {
  ygglog_debug(fmt);
  /* yggInfo(fmt); */
}
void ygg_log_error_f(const char* fmt) {
  ygglog_error(fmt);
}

// Methods for initializing channels
void* ygg_output_f(const char *name) {
  return (void*)yggOutput(name);
}

void* ygg_input_f(const char *name) {
  return (void*)yggInput(name);
}

void* yggAsciiFileOutput_f(const char *name) {
  return (void*)yggAsciiFileOutput(name);
}

void* yggAsciiFileInput_f(const char *name) {
  return (void*)yggAsciiFileInput(name);
}

void* yggAsciiTableOutput_f(const char *name, const char *format_str) {
  return (void*)yggAsciiTableOutput(name, format_str);
}

void* yggAsciiTableInput_f(const char *name) {
  return (void*)yggAsciiTableInput(name);
}

void* yggAsciiArrayOutput_f(const char *name, const char *format_str) {
  return (void*)yggAsciiArrayOutput(name, format_str);
}

void* yggAsciiArrayInput_f(const char *name) {
  return (void*)yggAsciiArrayInput(name);
}

void *yggPlyOutput_f(const char *name) {
  return (void*)yggPlyOutput(name);
}

void *yggPlyInput_f(const char *name) {
  return (void*)yggPlyInput(name);
}

void *yggObjOutput_f(const char *name) {
  return (void*)yggObjOutput(name);
}

void *yggObjInput_f(const char *name) {
  return (void*)yggObjInput(name);
}

// Methods for sending/receiving
int ygg_send_f(const void *yggQ, const char *data, const size_t len) {
  return ygg_send((const comm_t*)yggQ, data, len);
}

int ygg_recv_f(void *yggQ, char *data, const size_t len) {
  return ygg_recv((comm_t*)yggQ, data, len);
}

int ygg_send_var_f(const void *yggQ, int nargs, void *args) {
  if (args == NULL) {
    ygglog_error("ygg_send_var_f: args pointer is NULL.");
    return -1;
  }
  va_list_t ap = init_va_ptrs(nargs, (void**)args);
  return vcommSend((const comm_t*)yggQ, (size_t)nargs, ap);
}

int ygg_recv_var_f(void *yggQ, int nargs, void *args) {
  if (args == NULL) {
    ygglog_error("ygg_recv_var_f: args pointer is NULL.");
    return -1;
  }
  va_list_t ap = init_va_ptrs(nargs, (void**)args);
  ap.for_fortran = 1;
  return vcommRecv((comm_t*)yggQ, 0, (size_t)nargs, ap);
}

int ygg_recv_var_realloc_f(void *yggQ, int nargs, void *args) {
  if (args == NULL) {
    ygglog_error("ygg_recv_var_realloc_f: args pointer is NULL.");
    return -1;
  }
  va_list_t ap = init_va_ptrs(nargs, (void**)args);
  ap.for_fortran = 1;
  return vcommRecv((comm_t*)yggQ, 1, (size_t)nargs, ap);
}

// Ply interface
ply_t init_ply_f() {
  return init_ply();
}

void free_ply_f(void* p) {
  ply_t* c_p = (ply_t*)p;
  if (c_p != NULL) {
    free_ply(c_p);
    free(c_p);
    p = NULL;
  }
}

ply_t copy_ply_f(ply_t p) {
  return copy_ply(p);
}

void display_ply_indent_f(ply_t p, const char *indent) {
  display_ply_indent(p, indent);
}

void display_ply_f(ply_t p) {
  display_ply(p);
}

// Obj interface
obj_t init_obj_f() {
  return init_obj();
}

void free_obj_f(void* p) {
  obj_t* c_p = (obj_t*)p;
  if (c_p != NULL) {
    free_obj(c_p);
    free(c_p);
    p = NULL;
  }
}

obj_t copy_obj_f(obj_t p) {
  return copy_obj(p);
}

void display_obj_indent_f(obj_t p, const char *indent) {
  display_obj_indent(p, indent);
}

void display_obj_f(obj_t p) {
  display_obj(p);
}
