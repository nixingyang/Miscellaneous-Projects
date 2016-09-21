### Sequence Classification

#### Overview
This directory contains Python implementation which is capable of classifying sequence of inputs. As shown bellow, the data set consists of samples which belong to four unique labels. Since LSTM is widely used to model the temporal information, this project explores the possibility of utilizing LSTM to address a Sequence Classification problem while the order of input sequence has no effect on the prediction.
![data_distribution](Sequence%20Classification/data_distribution.png)

The following figures illustrate the loss/accuracy of the training/validation data set throughout the training procedure.
![loss](Sequence%20Classification/loss.png)
![acc](Sequence%20Classification/acc.png)
![val_loss](Sequence%20Classification/val_loss.png)
![val_acc](Sequence%20Classification/val_acc.png)
