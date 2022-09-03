import tensorflow as tf
import tensorflow_text as text


hypotheses = tf.ragged.constant([['captain', 'of', 'the', 'delta', 'flight'],
                                 ['the', '1990', 'transcript']])
references = tf.ragged.constant([['delta', 'air', 'lines', 'flight'],
                                 ['this', 'concludes', 'the', 'transcript']])


result = text.metrics.rouge_l(hypotheses, references)
print('F-Measure: %s' % result.f_measure)
print('P-Measure: %s' % result.p_measure)
print('R-Measure: %s' % result.r_measure)



# Compute ROUGE-L with alpha=0
result = text.metrics.rouge_l(hypotheses, references, alpha=0)
print('F-Measure (alpha=0): %s' % result.f_measure)
print('P-Measure (alpha=0): %s' % result.p_measure)
print('R-Measure (alpha=0): %s' % result.r_measure)



# Compute ROUGE-L with alpha=1
result = text.metrics.rouge_l(hypotheses, references, alpha=1)
print('F-Measure (alpha=1): %s' % result.f_measure)
print('P-Measure (alpha=1): %s' % result.p_measure)
print('R-Measure (alpha=1): %s' % result.r_measure)
