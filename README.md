# aspectExtractWithDependencyFeature
implement "Lifelong Learning CRF for Supervised Aspect Extraction"

# run
./run.sh ./dataout

# baseline result:
processed 2768 tokens with 176 phrases; found: 122 phrases; correct: 84.
accuracy:  94.54%; precision:  68.85%; recall:  47.73%; FB1:  56.38
             TERM: precision:  68.85%; recall:  47.73%; FB1:  56.38  122
             
# lifelong result:
processed 2768 tokens with 176 phrases; found: 158 phrases; correct: 104.
accuracy:  94.94%; precision:  65.82%; recall:  59.09%; FB1:  62.28
             TERM: precision:  65.82%; recall:  59.09%; FB1:  62.28  158
