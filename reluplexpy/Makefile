# \file Makefile
# \verbatim
# Top contributors (to current version):
#   Guy Katz
#   Kyle Julian
# This file is part of the Reluplex project.
# Copyright (c) 2016-2017 by the authors listed in the file AUTHORS
# (in the top-level source directory) and their institutional affiliations.
# All rights reserved. See the file COPYING in the top-level source
# directory for licensing information.\endverbatim
#

ROOT_DIR = .
PROJECT_DIR = $(ROOT_DIR)/..
GLPK_DIR = $(PROJECT_DIR)/glpk-4.60
PYBIND11_INCLUDES = $(shell python3 -m pybind11 --includes)
SUBDIRS += \

LOCAL_INCLUDES += \
	$(PROJECT_DIR)/common \
	$(GLPK_DIR)/installed/include \
	$(PROJECT_DIR)/reluplex \

LINK_FLAGS += \
	-L$(GLPK_DIR)/installed/lib

LOCAL_LIBRARIES += \
	glpk
    
SUFFIX = $(shell python-config --extension-suffix)
API_NAME = $(addprefix ReluplexCore, $(SUFFIX))

SOURCES += \
	ReluplexCore.cpp \

TARGET = $(API_NAME)

include Rules.mk

#
# Local Variables:
# compile-command: "make -C .. "
# End:
#
