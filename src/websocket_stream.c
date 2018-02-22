// WEBSOCKET_STREAM
// Functions created with the purpose of streaming live video/audio
// data through a websocket. This websocket will be streaming on port
// asynchronously from the rest of the program. In this code, we
// will suppose a message has already been generated, and is ready for
// streaming.
#ifndef WEBSOCKET_STREAM
#define WEBSOCKET_STREAM

#include <stdio.h>
#include <websock/websock.h>
#include <pthread.h>
#include <string.h>

#endif

int streaming_connect_cb(libwebsock_client_state *state) {
	frpintf(stderr, "New connection with socket descriptor: %d\n", state->sockfd);
	while(1){
		libwebsock_send_text(state, "streaming!\n");
	}
}

int createWebSocket(char* ip, char* port){
	libwebsock_context *ctx = NULL;
	ctx = libwebsock_init();
	if(ctx == NULL){
		print(stderr, "Error during libwebsock_init.\n");
		exit(1);
	}
	ctx->onopen = streaming_connect_cb;
	libwebsock_bind(ctx, ip, port);
	libwebsock_wait(ctx);
}
