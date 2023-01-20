"""An Azure RM Python Pulumi program"""

import pulumi_azure_native.network as network
import pulumi_azure_native as azure_native

# Create an Azure Resource Group


resource_group = azure_native.resources.get_resource_group("TF_automation_try-lorena")

network_security_group = azure_native.network.NetworkSecurityGroup("edk-vm-eikon-psecg-test01-lor",
    location=resource_group.location,
    network_security_group_name="edk-vm-eikon-psecg-test01-lor",
    resource_group_name=resource_group.name,
    security_rules=[{
        "access": "Allow",
        "destinationPortRange": "3389",
        "direction": "Inbound",
        "name": "Allow-RDC",
        "priority": 300,
        "protocol": "Tcp",
        "sourceAddressPrefix": "*",
        "sourcePortRange": "*",
        "destinationAddressPrefix": "*",

    }])


#insert network interface creation: name 
net = network.VirtualNetwork(
    "vm-eikon-network-test01-lor",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["172.17.0.0/24"],
    ),
    subnets=[network.SubnetArgs(
        name="vm-eikon-subnet-test01-lor",
        address_prefix="172.17.0.0/26",
        network_security_group= network.NetworkSecurityGroupArgs(
        id=network_security_group.id 
    ),
    )])

public_ip = network.PublicIPAddress(
    "vm-eikon-publicip-test01-lor",
    resource_group_name=resource_group.name,
    public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC)

network_iface = network.NetworkInterface(
    "vm-eikon-nic-test01-lor",
    resource_group_name=resource_group.name,
    location = resource_group.location,
    network_security_group= network.NetworkSecurityGroupArgs(
       id=network_security_group.id 
    ),
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="vm-eikon-ipconfig-test01-lor",
        subnet=network.SubnetArgs(id=net.subnets[0].id),
        private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
    )])



virtual_machine = azure_native.compute.VirtualMachine("edk-vm-eikon-test01-lor",
    hardware_profile=azure_native.compute.HardwareProfileArgs(
        vm_size="Standard_B2ms",
    ),
    location="northeurope",
    network_profile=azure_native.compute.NetworkProfileArgs(
        network_interfaces=[azure_native.compute.NetworkInterfaceReferenceArgs(
            id=network_iface.id,
        )],
    ),
    security_profile=azure_native.compute.SecurityProfileArgs(
        encryption_at_host=True,
    ),
    os_profile=azure_native.compute.OSProfileArgs(
        admin_password="eikonUser4today",
        admin_username="eikon-user",
        computer_name="eikon-t01",
        windows_configuration={
            "patchSettings": azure_native.compute.PatchSettingsArgs(
                assessment_mode="AutomaticByPlatform",
                patch_mode="AutomaticByPlatform",
            ),
            "provisionVMAgent": True,
        },
    ),
    resource_group_name="TF_automation_try-lorena",
    storage_profile=azure_native.compute.StorageProfileArgs(
        image_reference=azure_native.compute.ImageReferenceArgs(
            offer="WindowsServer",
            publisher="MicrosoftWindowsServer",
            sku="2022-datacenter-azure-edition-core",
            version="latest",
        ),
        os_disk={
            "caching": azure_native.compute.CachingTypes.READ_WRITE,
            "createOption": "FromImage",
            "name": "myVMosdisk",
        },
    ),
    vm_name="edk-vm-eikon-t01")

jit_network_access_policy = azure_native.security.JitNetworkAccessPolicy("jitNetworkAccessPolicy",
    asc_location="northeurope",
    jit_network_access_policy_name="default",
    kind="Basic",
    resource_group_name="TF_automation_try-lorena",
    virtual_machines=[{
        "id": "/subscriptions/dd4d7b4d-18fa-4791-b242-0ac01a71b933/resourceGroups/TF_automation_try-lorena/providers/Microsoft.Compute/virtualMachines/edk-vm-eikon-t01",
        "ports": [
            azure_native.security.JitNetworkAccessPortRuleArgs(
               allowed_source_address_prefix="*",
                max_request_access_duration="PT3H",
                number=22,
                protocol="*",
            ),
            azure_native.security.JitNetworkAccessPortRuleArgs(
                allowed_source_address_prefix="*",
                max_request_access_duration="PT3H",
                number=3389,
                protocol="*",
            ),
            azure_native.security.JitNetworkAccessPortRuleArgs(
                allowed_source_address_prefix="*",
                max_request_access_duration="PT3H",
                number=5985,
                protocol="*",
            ),
            azure_native.security.JitNetworkAccessPortRuleArgs(
                allowed_source_address_prefix="*",
                max_request_access_duration="PT3H",
                number=5986,
                protocol="*",
            ),
        ],
    }])
