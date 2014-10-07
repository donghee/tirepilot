# Copyright 2011 Adam Green (http://mbed.org/users/AdamGreen/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
PROJECT=EegTire
GCC4MBED_DIR=../..
LIBS_PREFIX=
LIBS_SUFFIX=
#NO_FLOAT_SCANF=1
#NO_FLOAT_PRINTF=1
GCC4MBED_TYPE=Debug

ifeq "$(OS)" "Windows_NT"
COPY=copy
TARGET_LOC=d:
DEPLOY_COMMAND=$(COPY) LPC1768\$(PROJECT).bin $(TARGET_LOC)
else
COPY=cp
TARGET_LOC=''
DEPLOY_COMMAND=$(COPY) LPC1768/$(PROJECT).bin $(TARGET_LOC)
endif

include ../../build/gcc4mbed.mk
#include=$(GCC4MBED_DIR)/build/gcc4mbed.mk

.PHONY: all clean upload

upload: clean all
	$(DEPLOY_COMMAND)
