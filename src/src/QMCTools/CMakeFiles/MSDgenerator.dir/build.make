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
include src/QMCTools/CMakeFiles/MSDgenerator.dir/depend.make

# Include the progress variables for this target.
include src/QMCTools/CMakeFiles/MSDgenerator.dir/progress.make

# Include the compile flags for this target's objects.
include src/QMCTools/CMakeFiles/MSDgenerator.dir/flags.make

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o: src/QMCTools/CMakeFiles/MSDgenerator.dir/flags.make
src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o: QMCTools/MSDgenerator.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /ccs/home/zgu/proj/qmc/src/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o -c /ccs/home/zgu/proj/qmc/src/QMCTools/MSDgenerator.cpp

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.i"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -E /ccs/home/zgu/proj/qmc/src/QMCTools/MSDgenerator.cpp > CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.i

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.s"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && /sw/sith/ompi/1.6.5/rhel6_gnu4.7.1/bin/mpicxx  $(CXX_DEFINES) $(CXX_FLAGS) -S /ccs/home/zgu/proj/qmc/src/QMCTools/MSDgenerator.cpp -o CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.s

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.requires:
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.requires

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.provides: src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.requires
	$(MAKE) -f src/QMCTools/CMakeFiles/MSDgenerator.dir/build.make src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.provides.build
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.provides

src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.provides.build: src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o

# Object files for target MSDgenerator
MSDgenerator_OBJECTS = \
"CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o"

# External object files for target MSDgenerator
MSDgenerator_EXTERNAL_OBJECTS =

bin/MSDgenerator: src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o
bin/MSDgenerator: src/QMCTools/CMakeFiles/MSDgenerator.dir/build.make
bin/MSDgenerator: /sw/redhat6/acml/5.3.0/gfortran64/lib/libacml.a
bin/MSDgenerator: /ccs/compilers/gcc/rhel6-x86_64/4.7.1/lib64/libgfortran.so
bin/MSDgenerator: /ccs/home/zgu/adioshub/adios_sith/lib/libadios.a
bin/MSDgenerator: /ccs/home/zgu/adioshub/adios_sith/lib/libadios.a
bin/MSDgenerator: /usr/lib64/libm.a
bin/MSDgenerator: /sw/redhat6/mxml/2.6/rhel6_gnu4.7.1/lib/libmxml.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdspaces.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdscommon.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdart.a
bin/MSDgenerator: /usr/lib64/librdmacm.so
bin/MSDgenerator: /usr/lib64/libibverbs.so
bin/MSDgenerator: lib/libmocommon.a
bin/MSDgenerator: lib/libqmcbase.a
bin/MSDgenerator: lib/libqmcutil.a
bin/MSDgenerator: /ccs/home/zgu/Software_sith/lib/libxml2.a
bin/MSDgenerator: /sw/redhat6/hdf5-parallel/1.8.11/rhel6.4_gnu4.7.1/lib/libhdf5.a
bin/MSDgenerator: /sw/redhat6/szip/2.1/rhel6_gnu4.7.1/lib/libsz.so
bin/MSDgenerator: /ccs/home/zgu/Software_sith/lib/libfftw3.a
bin/MSDgenerator: lib/libeinspline.a
bin/MSDgenerator: lib/liboompi.a
bin/MSDgenerator: /sw/redhat6/acml/5.3.0/gfortran64/lib/libacml.a
bin/MSDgenerator: /ccs/compilers/gcc/rhel6-x86_64/4.7.1/lib64/libgfortran.so
bin/MSDgenerator: /ccs/home/zgu/adioshub/adios_sith/lib/libadios.a
bin/MSDgenerator: /usr/lib64/libm.a
bin/MSDgenerator: /sw/redhat6/mxml/2.6/rhel6_gnu4.7.1/lib/libmxml.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdspaces.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdscommon.a
bin/MSDgenerator: /sw/redhat6/dataspaces/1.2.0/rhel6_gnu4.7.1/lib/libdart.a
bin/MSDgenerator: /usr/lib64/librdmacm.so
bin/MSDgenerator: /usr/lib64/libibverbs.so
bin/MSDgenerator: src/QMCTools/CMakeFiles/MSDgenerator.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX executable ../../bin/MSDgenerator"
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/MSDgenerator.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
src/QMCTools/CMakeFiles/MSDgenerator.dir/build: bin/MSDgenerator
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/build

src/QMCTools/CMakeFiles/MSDgenerator.dir/requires: src/QMCTools/CMakeFiles/MSDgenerator.dir/MSDgenerator.cpp.o.requires
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/requires

src/QMCTools/CMakeFiles/MSDgenerator.dir/clean:
	cd /ccs/home/zgu/proj/qmc/src/src/QMCTools && $(CMAKE_COMMAND) -P CMakeFiles/MSDgenerator.dir/cmake_clean.cmake
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/clean

src/QMCTools/CMakeFiles/MSDgenerator.dir/depend:
	cd /ccs/home/zgu/proj/qmc/src && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /ccs/home/zgu/proj/qmc /ccs/home/zgu/proj/qmc/src/QMCTools /ccs/home/zgu/proj/qmc/src /ccs/home/zgu/proj/qmc/src/src/QMCTools /ccs/home/zgu/proj/qmc/src/src/QMCTools/CMakeFiles/MSDgenerator.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : src/QMCTools/CMakeFiles/MSDgenerator.dir/depend

