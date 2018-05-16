==================
ec2 linux patching
==================

About
-----

ec2-patching enables ssh access to linux ec2 instances dispersed across vpcs and accounts.

Features:

- automatically sets up and cleans up a bastion ec2 instance and needed security group rules to ssh into vpc instances.
- lists vpcs (todo)
- lists instances summary (todo)


Usage
-----

ec2-patching help::

  Usage: ec2-patching [OPTIONS] COMMAND [ARGS]...

  Options:
    --profile TEXT  the aws credential profile
    --region TEXT   the aws region. Defaults to us-west-2
    --help          Show this message and exit.
  
    Commands:
      bastion  Work with the bastion


bastion command usage::

  Usage: ec2-patching bastion [OPTIONS] ACTION
  
    Work with the bastion

  Options:
    --allow-ip TEXT  the bastion ingress ip address
    --ami-id TEXT    deploy the basiton using the given ami id
    --name TEXT      the name of the bastion related resources
    --vpc-id TEXT    [required]
    --help           Show this message and exit.



Examples
--------

Render the bastion instance and vpc security group ingress rules cf template  using the bastion get-template command::

  $ profile=${profile:-ccctc-infiniti-sandbox}
  $ vpc_id=${vpc_id:-vpc-56b3952f}
  $ ec2-patching --region us-west-2 --profile $profile bastion get-template \
        --allow-ip 72.201.74.192 \
        --ami-id ami-55555 \
        --name bastion \
        --vpc-id $vpc_id

