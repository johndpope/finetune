import numpy as np

from finetune.config import MAX_LENGTH, BATCH_SIZE
from finetune.lm_base import LanguageModelBase


class LanguageModelGeneralAPI(LanguageModelBase):

    def __init__(self, autosave_path, max_length=MAX_LENGTH, verbose=True):
        super().__init__(autosave_path=autosave_path, max_length=max_length, verbose=verbose)
        self.is_classification = None

    def _text_to_ids(self, *Xs, max_length=None):
        max_length = max_length or self.max_length
        question_answer_pairs = self.encoder.encode_multi_input(*Xs, max_length=max_length)
        tokens, mask = self._array_format(question_answer_pairs)
        return tokens, mask

    def finetune(self, Xs, Y, batch_size=BATCH_SIZE, val_size=0.05, val_interval=150):
        """
        :param Xs: An iterable of lists or array of text, shape [batch, n_inputs, tokens]
        :param Y: integer or string-valued class labels. It is necessary for the items of Y to be sortable.
        :param batch_size: integer number of examples per batch. When N_GPUS > 1, this number
                           corresponds to the number of training examples provided to each GPU.
        :param val_size: Float fraction or int number that represents the size of the validation set.
        :param val_interval: The interval for which validation is performed, measured in number of steps.
        """
        self.is_classification = self.is_classification or not np.array(Y).dtype == 'float'  # problem type inferrence.
        return self._finetune(*list(zip(*Xs)), Y=Y, batch_size=batch_size, val_size=val_size, val_interval=val_interval)

    def predict(self, Xs, max_length=None):
        """
        Produces a list of most likely class labels as determined by the fine-tuned model.

        :param Xs: An iterable of lists or array of text, shape [batch, n_inputs, tokens]
        :param max_length: the number of tokens to be included in the document representation.
                           Providing more than `max_length` tokens as input will result in truncation.
        :returns: list of class labels.
        """
        return self._predict(*list(zip(*Xs)), max_length=max_length)

    def predict_proba(self, Xs, max_length=None):
        """
        Produces a probability distribution over classes for each example in X.

        :param Xs: An iterable of lists or array of text, shape [batch, n_inputs, tokens]
        :param max_length: the number of tokens to be included in the document representation.
                           Providing more than `max_length` tokens as input will result in truncation.
        :returns: list of dictionaries.  Each dictionary maps from a class label to its assigned class probability.
        """
        return self._predict_proba(*list(zip(*Xs)), max_length=max_length)

    def featurize(self, Xs, max_length=None):
        """
        Embeds inputs in learned feature space. Can be called before or after calling :meth:`finetune`.

        :param Xs: An iterable of lists or array of text, shape [batch, n_inputs, tokens]
        :param max_length: the number of tokens to be included in the document representation.
                           Providing more than `max_length` tokens as input will result in truncation.
        :returns: np.array of features of shape (n_examples, embedding_size).
        """
        return self._featurize(*list(zip(*Xs)), max_length=max_length)