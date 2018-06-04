==================
ec2 linux patching
==================

About
-----

ec2-patching enables ssh access to linux ec2 instances dispersed across vpcs and accounts.

Features:

- automatically creates and deletes a bastion ec2 instance and needed security group rules to ssh into all vpc instances.
- lists bastions summary
- lists vpcs summary
- lists ec2 instances (todo)
- generates ssh config and ansible inventory (todo)
- ssh bastion
- ssh instance through bastion (todo)


Usage
-----

ec2-patching help::

  Usage: ec2-patching [OPTIONS] COMMAND [ARGS]...
  
  
  
  Options:
    --log-level TEXT  the logging level
    --profile TEXT    the aws credential profile
    --region TEXT     the aws region. Defaults to us-west-2
    --help            Show this message and exit.
  
  Commands:
    bastion  Commands for managing a bastion ec2 instance...
    vpc      Commands for viewing vpc resources


bastion commands::

  Usage: ec2-patching bastion [OPTIONS] COMMAND [ARGS]...
  
    Commands for managing a bastion ec2 instance and security group rules
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    create        Creates the bastion cloudformation stack
    delete        Deletes the bastion cloudformation stack
    gen-template  Generates the bastion cloudformation template
    list          List bastions
    ssh           ssh into the bastion instance

vpc commands::
  
  Usage: ec2-patching vpc [OPTIONS] COMMAND [ARGS]...
  
    Commands for viewing vpc resources
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    list  List vpcs


Examples
--------

Generate the bastion cloudformation template::

  $ ec2-patching --region us-west-2 --profile -ccctc-infiniti-sandbox  bastion gen-template --name bastion --key-name bastion --vpc-id -vpc-56b3952f


Create the bastion::

  $ ec2-patching --profile ccc-apply-nonproduction bastion create --vpc-id vpc-4f215a28 --name vpc-sprawler --ssh-public-key "$(cat demo.pub )"
    ...
    ...
  $ ec2-patching --profile ccc-apply-nonproduction bastion list
    instance_id          public_ip         sg_ingress_rules  sg_id        name          vpc_id        stack_creation_time               private_ip
    -------------------  --------------  ------------------  -----------  ------------  ------------  --------------------------------  -------------
    i-03f6c8a4346064a94  34.219.208.161                  47  sg-3d980e4c  vpc-sprawler  vpc-4f215a28  2018-06-04 04:28:11.834000+00:00  10.206.31.169


list vpcs summary::

  $ ec2-patching --profile ccctc-primary vpc list
    vpc_id                 tag_name                              cidr              default_vpc    has_natgw    has_igw      enis_prv    enis_pub    eni_eips    enis_total    sgs_total    subnets_pub    subnets_total  tags
    ---------------------  ------------------------------------  ----------------  -------------  -----------  ---------  ----------  ----------  ----------  ------------  -----------  -------------  ---------------  ------
    vpc-26da9941           cvc2-ci                               172.21.16.0/25    False          False        True                0           5           3             5            9              3                3
    vpc-76151612           PRIMARY-HUB                           172.30.240.0/20   False          True         True               16          26          21            42           33              3                6
    vpc-974978f0           CCC Security Center R53 Health Check  172.16.0.0/16     False          False        True                0           0           0             0            2              2                2
    vpc-7eb2e819           openmdm vpc qa                        172.16.20.0/25    False          False        False               0           0           0             0            2              0                0
    vpc-0d63e16a           ExExchange-Pilot                      172.18.20.128/26  False          False        True                0          12           9            12            6              2                2
    vpc-7ecf1218           sonarqube                             172.16.20.0/25    False          False        True                0           4           3             4            4              3                3
    vpc-322fa255           edex-qa                               172.19.16.128/26  False          False        True                0           4           3             4            6              2                2
    vpc-8724ede3           InfoSec                               10.0.0.0/20       False          True         True               19          15           1            34           23              1                2
    vpc-3fb03c5a           Default                               172.31.0.0/16     True           False        True                8          48          22            56           96              3                3
    vpc-d1c31fb7           QA-MISC                               172.19.24.0/21    False          True         True               34          45          45            79           62              3                6
    vpc-03efbb67           ccc_assess_scratch                    10.0.0.0/24       False          False        False               0           0           0             0            1              0                0
    vpc-ee3c0a8a           Datalake-test                         172.88.0.0/16     False          True         True                9           6           4            15           22              2                6
    vpc-d47254b3           glue-vpc                              172.21.18.0/24    False          True         True                1           1           1             2            1              2                4
    vpc-f3b19f95           CCC-DataCenter                        192.168.2.0/23    False          True         True                0           1           1             1            1              1                3
    vpc-0dfef9fa1c17a6763  sonarcubetest                         10.0.0.0/24       False          False        False               1           0           0             1            2              0                1
    vpc-3e83b25a           CourseExchange-QA                     172.31.0.0/16     False          False        True                2           1           1             3            9              0                2
    vpc-dffe22b9           CI-MISC                               172.21.24.0/21    False          True         True               30          43          43            73           70              3                6
    vpc-df0588b8           edex-ci                               172.21.16.128/26  False          False        True                0           6           5             6            6              2                2
    vpc-35793452           CVC2-qa                               172.21.16.0/25    False          False        True                0           5           3             5            6              3                3
    vpc-6c57660b           WorkSpaces VPC                        10.0.0.0/16       False          True         True                9           1           1            10            7              1                3
