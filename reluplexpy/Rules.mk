# \file Rules.mk
# \verbatim
# Top contributors (to current version):
#   Guy Katz
# This file is part of the Reluplex project.
# Copyright (c) 2016-2017 by the authors listed in the file AUTHORS
# (in the top-level source directory) and their institutional affiliations.
# All rights reserved. See the file COPYING in the top-level source
# directory for licensing information.\endverbatim
#

#
# Utilities
#

#
# Utilities
#

COMPILE = c++ -std=c++11 -O3 -fPIC
LINK 	= c++ -std=c++11 -O3 -fPIC -shared -Wl,-undefined,dynamic_lookup
RM	= rm
GFIND 	= find
ETAGS	= etags
GREP 	= grep
XARGS	= xargs
CP	= cp

PERL 	= perl
TAR	= tar
UNZIP	= unzip


#COMPILE = g++
#LINK 	= g++

#
# Unzipping
#

%.unzipped: %.tar.bz2
	$(TAR) xjvf $<
	touch $@

%.unzipped: %.zip
	$(UNZIP) $<
	touch $@

#
# Compiling C/C++
#

LOCAL_INCLUDES += \
	. \
	$(COMMON_DIR) \
	$(CXXTEST_DIR) \

CFLAGS += \
	-MMD \
	-Wall \
	-Wextra \
	-Werror \
	-Wno-deprecated \
	\
	-g \

%.obj: %.cpp
	@echo "CC\t" $@
	@$(COMPILE) -c -o $@ $< $(CFLAGS) $(addprefix -I, $(LOCAL_INCLUDES)) $(PYBIND11_INCLUDES)

%.obj: %.cxx
	@echo "CC\t" $@
	@$(COMPILE) -c -o $@ $< $(CFLAGS) $(addprefix -I, $(LOCAL_INCLUDES)) $(PYBIND11_INCLUDES)

#
# Linking C/C++
#

SYSTEM_LIBRARIES += \

#
# Compiling Elf Files
#

ifneq ($(TARGET),)

DEPS = $(SOURCES:%.cpp=%.d)

OBJECTS = $(SOURCES:%.cpp=%.obj)

$(TARGET): $(OBJECTS)
	@echo "LD\t" $@
	@$(LINK) $(LINK_FLAGS) -o $@ $^ $(addprefix -l, $(SYSTEM_LIBRARIES)) $(addprefix -l, $(LOCAL_LIBRARIES))

#%.elf: $(OBJECTS)
#	$(LINK) $(LINK_FLAGS) -o $@ $^ $(addprefix -l, $(SYSTEM_LIBRARIES)) $(addprefix -l, $(LOCAL_LIBRARIES))

.PRECIOUS: %.obj

endif

#
# Recursive Make
#

all: $(SUBDIRS:%=%.all) $(TARGET) $(TEST_TARGET)

clean: $(SUBDIRS:%=%.clean) clean_directory

%.all:
	$(MAKE) -C $* all

%.clean:
	$(MAKE) -C $* clean

clean_directory:
	$(RM) -f *~ *.cxx *.obj *.d $(TARGET) $(TEST_TARGET)

ifneq ($(DEPS),)
-include $(DEPS)
endif

#
# Local Variables:
# compile-command: "make -C . "
# End:
#
