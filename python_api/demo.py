from shipyard_api import *
import secrets


ctx = ApiContext("mhamilton723/conda-tensorflow",
                 "fileshare",
                 "marhamilbatchsouth",
                 secrets.batch_key,
                 "https://marhamilbatchsouth.southcentralus.batch.azure.com",
                 "marhamilsouthcentral2",
                 secrets.storage_key)

pool = Pool(ctx, "tensorflow-pool", 4, "STANDARD_D11_V2")

skipgram_job = Job("word2vec", "/fileshare/PycharmProjects/Adversarial_SkipGram/src/word2vec.py")

pool.grid_submit(skipgram_job, {"subtract_log_q": [True], "loss_name": ['sampled_softmax']})
