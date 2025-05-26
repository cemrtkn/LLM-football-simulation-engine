# LLM-football-simulation-engine
This project is an attempt at transforming an LLM into a football simulation engine. Envisioning a functionality similar to conventional simulation engines (more specifically Football Manager), it is exploration of how a relatively small language model Mistral-7b-v0.3 base model can be used to generate realistic sequences of match events. The model was fine-tuned with the QLoRa paradigm so an [adapter](https://huggingface.co/cemrtkn/llm-football-simulator) on top of the model at a quantized precision was the end product.

## Data
The raw structured events data can be found at [Statsbomb's open-data repo](https://github.com/statsbomb/open-data).

With some filtering and preprocessing of the data it was ready to be used to finetune an LLM. Only a 50K sample subset of the whole 3M sample dataset was used at the end.

## Resources
The training was done on an A100 and it took around 18 hours.

## How to use

```
from adapters import list_adapters, get_adapter_info
from transformers import ( 
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM
)
from tqdm import tqdm
import torch
from huggingface_hub import login

# log into hf to get access to the adapter
login(token=hf_token)

# init configs
model_name = "mistralai/Mistral-7B-v0.3"
device_map = {"":0}

use_4bit = True
bnb_4bit_compute_dtype = "float16"
bnb_4bit_quant_type = "nf4"
use_nested_quant = False

compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

bnb_config = BitsAndBytesConfig(
    load_in_4bit = use_4bit,
    bnb_4bit_quant_type = bnb_4bit_quant_type,
    bnb_4bit_compute_dtype = compute_dtype,
    bnb_4bit_use_double_quant = use_nested_quant,)


# load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code = True)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config = bnb_config,
    device_map = device_map,
)


model.load_adapter("cemrtkn/llm-football-simulator")


input_text = """This is a sequence of football match events.
Time: 00:00:00.000 | Event: Half Start
"""
seq_list = input_text.split('\n')
match_list = []
for i in tqdm(range(5)):
    input_text = '\n'.join(seq_list)
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")  # Ensure tensors are on the right device
    # hacky way to generate 
    output = model.generate(**inputs, max_new_tokens=100, do_sample=True ,temperature=1, pad_token_id=tokenizer.eos_token_id)
    
    prediction = tokenizer.decode(output[0], skip_special_tokens=True).split('\n')[-2]
    print(prediction)

```



For detailed overview of the methodology and insights, you can look at this [medium blog](https://medium.com/@cemrtkn/llm-as-a-simulator-fine-tuning-llms-to-simulate-football-matches-537c0e678b55).