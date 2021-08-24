docker build  \
--build-arg MODEL_DIR=MODELS/model_MULTI_DISTILBERT_unfreeze_last_layers_5epoch_C4C_adresses \
-t c4c_term_extraction  \
-f Dockerfile .