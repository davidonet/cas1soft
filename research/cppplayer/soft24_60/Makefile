# location of 

CC = g++
CFLAGS = -DDEBUG  -g `sdl-config --cflags`
TARGET = soft2460
SRC = $(wildcard *.cc)
OBJ = $(SRC:%.cc=%.o)
LIB = `sdl-config --libs` -lavutil -lavcodec -lswscale -lz -lm -lboost_filesystem -lboost_date_time -pthread -lccgnu2 -lSDL_image  -lSDL_Pango -lavformat
INC = -Iffmpeg -D__STDC_CONSTANT_MACROS


all: $(TARGET)

.SUFFIXES: .cc
%.o: %.cc
	$(CC) $(CFLAGS) $(INC) -c $< -o $@

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LIB)

clean:
	rm -f *.o $(TARGET) core *~
