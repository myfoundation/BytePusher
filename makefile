CC = gcc
CC_OPTS = -std=c99 -O2 -Werror -Wall -Wextra -Wpedantic
RAYLIB_PATH = raylib

windows:
	$(CC) $(CC_OPTS) bytepusher.c -o bytepusher.exe -I$(RAYLIB_PATH)/include $(RAYLIB_PATH)/lib/libraylib.a -lgdi32 -lwinmm

linux:
	$(CC) $(CC_OPTS) bytepusher.c -o bytepusher -lraylib -lGL -lm -lpthread -ldl -lrt -lX11
