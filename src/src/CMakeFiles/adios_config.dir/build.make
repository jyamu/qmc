# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /autofs/na4_sw/redhat6/cmake/2.8.11.2/rhel6.4_gnu4.4.7/bin/cmake

# The command to remove a file.
RM = /autofs/na4_sw/redhat6/cmake/2.8.11.2/rhel6.4_gnu4.4.7/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /ccs/home/zgu/proj/qmc

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /ccs/home/zgu/proj/qmc/src

# Include any dependencies generated for this target.
include src/CMakeFiles/adios_config.dir/depend.make

# Include the progress variables for this target.
include src/CMakeFiles/adios_config.dir/progress.make

# Include the compile flags for this target's objects.
include src/CMakeFiles/adios_config.dir/flags.make

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o: src/CMakeFiles/adios_config.dir/flags.make
src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o: ADIOS/ADIOS_config.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /ccs/home/zgu/proj/qmc/src/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o"
	cd /ccs/home/zgu/proj/qmc/src/src && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o -c /ccs/home/zgu/proj/qmc/src/ADIOS/ADIOS_config.cpp

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.i"
	cd /ccs/home/zgu/proj/qmc/src/src && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -E /ccs/home/zgu/proj/qmc/src/ADIOS/ADIOS_config.cpp > CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.i

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.s"
	cd /ccs/home/zgu/proj/qmc/src/src && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -S /ccs/home/zgu/proj/qmc/src/ADIOS/ADIOS_config.cpp -o CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.s

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.requires:
.PHONY : src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.requires

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.provides: src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.requires
	$(MAKE) -f src/CMakeFiles/adios_config.dir/build.make src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.provides.build
.PHONY : src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.provides

src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.provides.build: src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o

# Object files for target adios_config
adios_config_OBJECTS = \
"CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o"

# External object files for target adios_config
adios_config_EXTERNAL_OBJECTS =

lib/libadios_config.a: src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o
lib/libadios_config.a: src/CMakeFiles/adios_config.dir/build.make
lib/libadios_config.a: src/CMakeFiles/adios_config.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX static library ../lib/libadios_config.a"
	cd /ccs/home/zgu/proj/qmc/src/src && $(CMAKE_COMMAND) -P CMakeFiles/adios_config.dir/cmake_clean_target.cmake
	cd /ccs/home/zgu/proj/qmc/src/src && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/adios_config.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
src/CMakeFiles/adios_config.dir/build: lib/libadios_config.a
.PHONY : src/CMakeFiles/adios_config.dir/build

src/CMakeFiles/adios_config.dir/requires: src/CMakeFiles/adios_config.dir/ADIOS/ADIOS_config.cpp.o.requires
.PHONY : src/CMakeFiles/adios_config.dir/requires

src/CMakeFiles/adios_config.dir/clean:
	cd /ccs/home/zgu/proj/qmc/src/src && $(CMAKE_COMMAND) -P CMakeFiles/adios_config.dir/cmake_clean.cmake
.PHONY : src/CMakeFiles/adios_config.dir/clean

src/CMakeFiles/adios_config.dir/depend:
	cd /ccs/home/zgu/proj/qmc/src && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /ccs/home/zgu/proj/qmc /ccs/home/zgu/proj/qmc/src /ccs/home/zgu/proj/qmc/src /ccs/home/zgu/proj/qmc/src/src /ccs/home/zgu/proj/qmc/src/src/CMakeFiles/adios_config.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : src/CMakeFiles/adios_config.dir/depend

