# coding: utf-8

# PYTHON
from collections import defaultdict
from heapq import nlargest
from string import punctuation

# THIRD PARTY LIB
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


class FrequencySummarizer:
    """
        The idea is to generate a summarizer from a given text based on
        the analysis of words frequency.

        Parameters used: min_frequency & max_frequency
        Words that have a frequency term lower 'freq' such as:
            freq < min_frequency or freq > max_frequency
        will be ignored.

        Note: If you have a few very long sentences...
        With a lot of keywords in it...
        They will be for sure in your summary and sometimes,
        it's not what you're expect.
        You can end up with an example which is not the core of your article
        you want to summarize.
        Further work could be done to address this.
    """

    def __init__(self, min_frequency=0.1, max_frequency=0.9, max_length_sentences=140):
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        self.max_length_sentences = max_length_sentences
        self.common_words = set(stopwords.words('english') + list(punctuation))

    def _is_frequency_neglectable(self, frequency):
        """
            We filter out too common or uncommon words.
            Note: min_frequency and max_frequency are set empirically.
        """
        return frequency >= self.max_frequency or frequency <= self.min_frequency

    def _compute_words_frequency(self, tokenized_text):
        """
            Compute the frequency of each words.
            @param
            tokenized_text: a list of sentences already tokenized.

            Output:
            frequency, a frequency dictionary for each word.
        """
        frequency = defaultdict(int)
        for sentence in tokenized_text:
            for word in sentence:
                if word not in self.common_words:
                    frequency[word] += 1

        # frequencies normalization
        max_frequency = float(max(frequency.values()))
        for word in frequency:
            frequency[word] /= max_frequency

        # fitering uncommon words and too common words
        if self._is_frequency_neglectable(frequency[word]):
            del frequency[word]

        return frequency

    def _rank_sentences(self, tokenized_text, words_frequency):
        ranking = defaultdict(int)
        for counter, sentence in enumerate(tokenized_text):
            for word in sentence:
                if word in words_frequency:
                    ranking[counter] += words_frequency[word]
        return ranking

    def summarize(self, text, summary_length):
        """
            First, we tokenize the text. Sentences, then words.
            We eventually filter out long sentences (e.g. for twitter use)
            Second, we compute the word frequency
            Third, we rank the sentences with their word frequency
            Finally, we retrieve the highest ranked sentences.
        """
        sentences = [sentence for sentence in sent_tokenize(text) if len(sentence) < self.max_length_sentences]
        assert summary_length <= len(sentences)
        tokenized_text = [word_tokenize(sentence.lower()) for sentence in sentences]

        words_frequency = self._compute_words_frequency(tokenized_text)

        ranking = self._rank_sentences(tokenized_text, words_frequency)

        return [sentences[j] for j in nlargest(summary_length, ranking, key=ranking.get)]


if __name__ == '__main__':
    summarizer = FrequencySummarizer(min_frequency=0.05, max_frequency=0.95)
    text = """#my text to summarize. This is a bumb test. Nothing here."""
    print(summarizer.summarize(text, 2))
