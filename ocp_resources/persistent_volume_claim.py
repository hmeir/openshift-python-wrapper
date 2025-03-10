# -*- coding: utf-8 -*-

from ocp_resources.utils.constants import TIMEOUT_4MINUTES
from ocp_resources.resource import NamespacedResource


class PersistentVolumeClaim(NamespacedResource):
    """
    PersistentVolumeClaim object
    """

    api_version = NamespacedResource.ApiVersion.V1

    class Status(NamespacedResource.Status):
        BOUND = "Bound"

    class AccessMode:
        """
        AccessMode object.
        """

        RWO = "ReadWriteOnce"
        ROX = "ReadOnlyMany"
        RWX = "ReadWriteMany"

    class VolumeMode:
        """
        VolumeMode object
        """

        BLOCK = "Block"
        FILE = "Filesystem"

    def __init__(
        self,
        name=None,
        namespace=None,
        client=None,
        storage_class=None,
        accessmodes=None,
        volume_mode=VolumeMode.FILE,
        size=None,
        hostpath_node=None,
        teardown=True,
        yaml_file=None,
        delete_timeout=TIMEOUT_4MINUTES,
        pvlabel=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            namespace=namespace,
            client=client,
            teardown=teardown,
            yaml_file=yaml_file,
            delete_timeout=delete_timeout,
            **kwargs,
        )
        self.accessmodes = accessmodes
        self.volume_mode = volume_mode
        self.size = size
        self.hostpath_node = hostpath_node
        self.storage_class = storage_class
        self.pvlabel = pvlabel

    def to_dict(self) -> None:
        super().to_dict()
        if not self.kind_dict and not self.yaml_file:
            self.res.update({
                "spec": {
                    "volumeMode": self.volume_mode,
                    "accessModes": [self.accessmodes],
                    "resources": {"requests": {"storage": self.size}},
                }
            })
            """
            Hostpath-provisioner is "node aware", when using it,
            a node attribute on the claim must be introduced as follows.
            annotations:
              kubevirt.io/provisionOnNode: <specified_node_name>
            """
            if self.hostpath_node:
                self.res["metadata"]["annotations"] = {"kubevirt.io/provisionOnNode": self.hostpath_node}
            if self.storage_class:
                self.res["spec"]["storageClassName"] = self.storage_class

            if self.pvlabel:
                self.res["spec"]["selector"] = {"matchLabels": {"pvLabel": self.pvlabel}}

    def bound(self):
        """
        Check if PVC is bound

        Returns:
            bool: True if bound else False
        """
        self.logger.info(f"Check if {self.kind} {self.name} is bound")
        return self.status == self.Status.BOUND

    @property
    def selected_node(self):
        return self.instance.metadata.annotations.get("volume.kubernetes.io/selected-node")

    @property
    def use_populator(self):
        return self.instance.metadata.annotations.get(f"{self.ApiGroup.CDI_KUBEVIRT_IO}/storage.usePopulator") == "true"

    @property
    def prime_pvc(self):
        if self.use_populator:
            return PersistentVolumeClaim(
                name=f"prime-{self.instance.metadata.uid}",
                namespace=self.namespace,
                client=self.client,
            )
