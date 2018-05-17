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
    bastion  Commands for managing a bastion ec2 instance...
    list     Commands for listing ec2 resources

bastion command group usage::

  Usage: ec2-patching bastion [OPTIONS] COMMAND [ARGS]...
  
    Commands for managing a bastion ec2 instance and security group rules
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    create-stack  Creates the bastion cloudformation stack
    delete-stack  Deletes the bastion cloudformation stack
    gen-template  Generates the bastion cloudformation template


Examples
--------

Render the bastion instance and vpc security group ingress rules cf template  using the bastion gen-template command::

  $ profile=${profile:-ccctc-infiniti-sandbox}
  $ vpc_id=${vpc_id:-vpc-56b3952f}
  $ ec2-patching --region us-west-2 --profile $profile bastion gen-template \
        --allow-ip 72.201.74.192 \
        --ami-id ami-55555 \
        --name bastion \
        --key-name bastion \
        --vpc-id $vpc_id
