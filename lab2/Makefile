# Makefile for Cache Simulator
# CSE 3031 - Lab 2

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lm

TARGET = cachesim
SRC = cachesim.c
OBJ = $(SRC:.c=.o)

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ) $(LDFLAGS)

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJ) $(TARGET) *.out

# Clean all output files
cleanall: clean
	rm -f *.trace.out

# Help target
help:
	@echo "Cache Simulator Makefile"
	@echo "Available targets:"
	@echo "  all      - Build the cache simulator (default)"
	@echo "  clean    - Remove object files and executable"
	@echo "  cleanall - Remove object files, executable, and all .out files"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Usage: ./cachesim <config_file> <trace_file>"

.PHONY: all clean cleanall help
