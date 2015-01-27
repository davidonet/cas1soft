CC:=g++
INCLUDES:=$(shell pkg-config --cflags libavformat libavcodec libswscale libavutil sdl)
CFLAGS:=
LDFLAGS:=$(shell pkg-config --libs libavformat libavcodec libswscale libavutil sdl) -lm -llo
TARGET = soft2460
SRC = $(wildcard *.cc)
OBJ = $(SRC:%.cc=%.o)


all: $(TARGET)

%.o: %.cc
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJ) $(LIB)

clean:
	rm -f *.o $(TARGET) core *~