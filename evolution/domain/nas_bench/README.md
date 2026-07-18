## NAS-Bench
To run the NAS-Bench example, clone the nasbench repo, download the dataset, and add nasbench to your PYTHONPATH
```bash
git clone https://github.com/google-research/nasbench.git
export PYTHONPATH=`pwd`/nasbench:$PYTHONPATH
cd nasbench
pip install -e .
cd ../evolution/domain/nas_bench/
wget https://storage.googleapis.com/nasbench/nasbench_only108.tfrecord
 ```
