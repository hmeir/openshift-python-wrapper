from ocp_resources.utils.constants import TIMEOUT_4MINUTES
from ocp_resources.resource import NamespacedResource


class OperatorGroup(NamespacedResource):
    api_group = NamespacedResource.ApiGroup.OPERATORS_COREOS_COM

    def __init__(
        self,
        name=None,
        namespace=None,
        target_namespaces=None,
        teardown=True,
        client=None,
        yaml_file=None,
        delete_timeout=TIMEOUT_4MINUTES,
        **kwargs,
    ):
        """
        Args:
            target_namespaces(list): namespaces in which to generate required RBAC access for its member Operators.
        """
        super().__init__(
            name=name,
            namespace=namespace,
            client=client,
            teardown=teardown,
            yaml_file=yaml_file,
            delete_timeout=delete_timeout,
            **kwargs,
        )
        self.target_namespaces = target_namespaces

    def to_dict(self) -> None:
        super().to_dict()
        if not self.kind_dict and not self.yaml_file:
            self.res.update({"spec": {"targetNamespaces": self.target_namespaces}})
