# Pipeline of Deep Nuclei Parcellation

This is a pipeline that uses deep learning techniques to parcel brain nuclei based on tractography. It includes the entire process from dataset construction to nuclei parcellation and performance evaluation. In theory, it can be used to parcel any nuclear structures in the brain. 

Our paper [A Novel Deep Clustering Framework for Fine-Scale Parcellation of Amygdala Using DMRI Tractography](https://ieeexplore.ieee.org/document/10635363) has already been published in ISBI2024, demonstrating the effectiveness of this pipeline in amygdala parcellation.

The steps for using this pipeline are as follows:

1. Organize the data. 

    Before processing the data, it needs to be structured into a specific format. The data organization format we have defined is as follows: