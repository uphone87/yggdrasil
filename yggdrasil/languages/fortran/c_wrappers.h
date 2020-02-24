#ifndef YGG_FC_WRAPPERS_H_
#define YGG_FC_WRAPPERS_H_

#include "../C/YggInterface.h"

#ifdef __cplusplus /* If this is a C++ compiler, use C linkage */
extern "C" {
#endif

// Utilities
void ygg_c_free(void *x);
void ygg_log_info_f(const char* fmt);
void ygg_log_debug_f(const char* fmt);
void ygg_log_error_f(const char* fmt);
// Methods for initializing channels
void* ygg_output_f(const char *name);
void* ygg_input_f(const char *name);
void* yggAsciiFileOutput_f(const char *name);
void* yggAsciiFileInput_f(const char *name);
void* yggAsciiTableOutput_f(const char *name, const char *format_str);
void* yggAsciiTableInput_f(const char *name);
void* yggAsciiArrayOutput_f(const char *name, const char *format_str);
void* yggAsciiArrayInput_f(const char *name);
void *yggPlyOutput_f(const char *name);
void *yggPlyInput_f(const char *name);
void *yggObjOutput_f(const char *name);
void *yggObjInput_f(const char *name);
// Methods for sending/receiving
int ygg_send_f(const void *yggQ, const char *data, const size_t len);
int ygg_recv_f(void *yggQ, char *data, const size_t len);
int ygg_send_var_f(const void *yggQ, int nargs, void *args);
int ygg_recv_var_f(void *yggQ, int nargs, void *args);
int ygg_recv_var_realloc_f(void *yggQ, int nargs, void *args);
// Ply interface
ply_t init_ply_f();
void free_ply_f(void* p);
ply_t copy_ply_f(ply_t p);
void display_ply_indent_f(ply_t p, const char *indent);
void display_ply_f(ply_t p);
// Obj interface
obj_t init_obj_f();
void free_obj_f(void* p);
obj_t copy_obj_f(obj_t p);
void display_obj_indent_f(obj_t p, const char *indent);
void display_obj_f(obj_t p);

#ifdef __cplusplus /* If this is a C++ compiler, end C linkage */
}
#endif


#endif /*YGG_FC_WRAPPERS_H_*/
