# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import DatastoreType

from azure.ai.ml._schema.core.fields import NestedField, PathAwareSchema, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake

from .credentials import NoneCredentialsSchema, ServicePrincipalSchema


class OneLakeArtifactSchema(PathAwareSchema):
    artifact_name = fields.Str(required=True)
    artifact_type = fields.Str()


class OneLakeSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    type = StringTransformedEnum(
        allowed_values=DatastoreType.ONE_LAKE,
        casing_transform=camel_to_snake,
        required=True,
    )
    # required fields for OneLake
    one_lake_workspace_name = fields.Str(required=True)
    artifact = NestedField(OneLakeArtifactSchema)
    endpoint = fields.Str()
    # ServicePrincipal and UserIdentity are the two supported credential types
    credentials = UnionField(
        [
            NestedField(ServicePrincipalSchema),
            NestedField(NoneCredentialsSchema),
        ]
    )
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "OneLakeDatastore":
        from azure.ai.ml.entities import OneLakeDatastore

        return OneLakeDatastore(**data)
