# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: coordinator.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import computation_msgs_pb2 as computation__msgs__pb2
import registration_msgs_pb2 as registration__msgs__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='coordinator.proto',
  package='protoBuf',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x11\x63oordinator.proto\x12\x08protoBuf\x1a\x16\x63omputation-msgs.proto\x1a\x17registration-msgs.proto2S\n\x0fSiteCoordinator\x12@\n\x0cRegisterAlgo\x12\x14.protoBuf.SiteRegReq\x1a\x18.protoBuf.SiteAlgoRegRes\"\x00\x32\x9d\x01\n\x10\x43loudCoordinator\x12\x46\n\x0cRegisterAlgo\x12\x19.protoBuf.CloudAlgoRegReq\x1a\x19.protoBuf.CloudAlgoRegRes\"\x00\x12\x41\n\x07\x43ompute\x12\x18.protoBuf.ComputeRequest\x1a\x1a.protoBuf.ComputeResponses\"\x00\x62\x06proto3')
  ,
  dependencies=[computation__msgs__pb2.DESCRIPTOR,registration__msgs__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_SITECOORDINATOR = _descriptor.ServiceDescriptor(
  name='SiteCoordinator',
  full_name='protoBuf.SiteCoordinator',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=80,
  serialized_end=163,
  methods=[
  _descriptor.MethodDescriptor(
    name='RegisterAlgo',
    full_name='protoBuf.SiteCoordinator.RegisterAlgo',
    index=0,
    containing_service=None,
    input_type=registration__msgs__pb2._SITEREGREQ,
    output_type=registration__msgs__pb2._SITEALGOREGRES,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_SITECOORDINATOR)

DESCRIPTOR.services_by_name['SiteCoordinator'] = _SITECOORDINATOR


_CLOUDCOORDINATOR = _descriptor.ServiceDescriptor(
  name='CloudCoordinator',
  full_name='protoBuf.CloudCoordinator',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  serialized_start=166,
  serialized_end=323,
  methods=[
  _descriptor.MethodDescriptor(
    name='RegisterAlgo',
    full_name='protoBuf.CloudCoordinator.RegisterAlgo',
    index=0,
    containing_service=None,
    input_type=registration__msgs__pb2._CLOUDALGOREGREQ,
    output_type=registration__msgs__pb2._CLOUDALGOREGRES,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Compute',
    full_name='protoBuf.CloudCoordinator.Compute',
    index=1,
    containing_service=None,
    input_type=computation__msgs__pb2._COMPUTEREQUEST,
    output_type=computation__msgs__pb2._COMPUTERESPONSES,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_CLOUDCOORDINATOR)

DESCRIPTOR.services_by_name['CloudCoordinator'] = _CLOUDCOORDINATOR

# @@protoc_insertion_point(module_scope)
