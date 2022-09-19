# BodyTrack2D: A robust pill decomposition based approach for body tracking.

## About

This work was carried out under the supervision of [Prof. Jiju Poovvancheri](https://cs.smu.ca/~jiju/index.php/group-2/) at Saint Mary's University, Halifax, Canada as a part of the [MITACS](https://www.mitacs.ca/en/programs/globalink/globalink-research-internship) project.

A corresponding report can be found [here](https://sarosijbose.github.io/files/MITACS_final_report_sarosij_bose.pdf).

## Setup

Please follow the instructions regarding input data formats in the [masbpy](https://github.com/tudelft3d/masbpy) repository.

For setting the initial maximal ball radius, please go through [this paper](https://www.researchgate.net/publication/220067310_3D_medial_axis_point_approximation_using_nearest_neighbors_and_the_normal_field?enrichId=rgreq-bf4d8ed261be54f8ced4e12e3da0b6e2-XXX&enrichSource=Y292ZXJQYWdlOzIyMDA2NzMxMDtBUzoxMDM5ODkzMjAzNTU4NTRAMTQwMTgwNDM5NDgzMA%3D%3D&el=1_x_3&_esc=publicationCoverPdf) first.

1. It is recommended to initially setup a fresh virtual environment
```bash
python -m venv bdt2d
source activate env/bin/activate
```
2. Install the required packages.

```bash
pip install -r requirements.txt
```
3. Run the ```run.sh``` file. Set the 2D keypoint file paths and parameters accordingly.

4. Some sample output runs and their corresponding plots are present in the ```log``` and ```plots``` folder respectively.

## Acknowledgements

Parts of the codebase has been borrowed from the [masbpy](https://github.com/tudelft3d/masbpy) repository. We are grateful to the authors for making their work publicly available. 
