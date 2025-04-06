#!/bin/csh
csh << EOF
source /etc/profile.d/modules.csh
module load singularity
mkdir singularity
singularity pull ./singularity/langchain.sif docker://langchain/langchain
EOF