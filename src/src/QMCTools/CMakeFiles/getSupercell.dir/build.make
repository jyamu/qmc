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
include src/QMCTools/CMakeFiles/getSupercell.dir/depend.make

# Include the progress variables for this target.
include src/QMCTools/CMakeFiles/getSupercell.dir/progress.make

# Include the compile flags for this target's objects.
include src/QMCTools/CMakeFiles/getSupercell.dir/flags.make

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o: src/QMCTools/CMakeFiles/getSupercell.dir/flags.make
src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o: QMCTools/getSupercell.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /ccs/home/zgu/proj/qmc/src/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/getSupercell.dir/getSupercell.cpp.o -c /ccs/home/zgu/proj/qmc/src/QMCTools/getSupercell.cpp

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/getSupercell.dir/getSupercell.cpp.i"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -E /ccs/home/zgu/proj/qmc/src/QMCTools/getSupercell.cpp > CMakeFiles/getSupercell.dir/getSupercell.cpp.i

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/getSupercell.dir/getSupercell.cpp.s"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -S /ccs/home/zgu/proj/qmc/src/QMCTools/getSupercell.cpp -o CMakeFiles/getSupercell.dir/getSupercell.cpp.s

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.requires:
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.requires

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.provides: src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.requires
	$(MAKE) -f src/QMCTools/CMakeFiles/getSupercell.dir/build.make src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.provides.build
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.provides

src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.provides.build: src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o

# Object files for target getSupercell
getSupercell_OBJECTS = \
"CMakeFiles/getSupercell.dir/getSupercell.cpp.o"

# External object files for target getSupercell
getSupercell_EXTERNAL_OBJECTS =

bin/getSupercell: src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o
bin/getSupercell: src/QMCTools/CMakeFiles/getSupercell.dir/build.make
bin/getSupercell: /sw/redhat6/acml/5.3.0/gfortran64/lib/libacml.a
bin/getSupercell: /ccs/compilers/gcc/rhel6-x86_64/4.7.1/lib64/libgfortran.so
bin/getSupercell: /ccs/home/zgu/adioshub/adios_sith/lib/libadios.a
bin/getSupercell: /ccs/home/zgu/adioshub/adios_sith/lib/libadios.a
bin/getSupercell: /usr/lib64/libm.a
bin/getSupercell: /sw/redhat6/mxml/2.6/rhel6_gnu4.7.1/lib/libmxml.a
bin/getSupercell: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdspaces.a
bin/getSupercell: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdscommon.a
bin/getSupercell: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdart.a
bin/getSupercell: /usr/lib64/librdmacm.so
bin/getSupercell: /usr/lib64/libibverbs.so
bin/getSupercell: src/QMCTools/CMakeFiles/getSupercell.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX executable ../../bin/getSupercell"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/getSupercell.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
src/QMCTools/CMakeFiles/getSupercell.dir/build: bin/getSupercell
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/build

src/QMCTools/CMakeFiles/getSupercell.dir/requires: src/QMCTools/CMakeFiles/getSupercell.dir/getSupercell.cpp.o.requires
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/requires

src/QMCTools/CMakeFiles/getSupercell.dir/clean:
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && $(CMAKE_COMMAND) -P CMakeFiles/getSupercell.dir/cmake_clean.cmake
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/clean

src/QMCTools/CMakeFiles/getSupercell.dir/depend:
	cd /ccs/home/zgu/proj/qmc/src && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /ccs/home/zgu/proj/qmc /ccs/home/zgu/proj/qmc/src/QMCTools /ccs/home/zgu/proj/qmc/src /ccs/home/zgu/proj/qmc/src/src/QMCTools /ccs/home/zgu/proj/qmc/src/src/QMCTools/CMakeFiles/getSupercell.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : src/QMCTools/CMakeFiles/getSupercell.dir/depend

