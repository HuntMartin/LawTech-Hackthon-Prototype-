from transformers import DistilBertForQuestionAnswering, DistilBertTokenizerFast, Trainer, TrainingArguments
from datasets import load_dataset

model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizerFast.from_pretrained(model_name)
model = DistilBertForQuestionAnswering.from_pretrained(model_name)



dataset = load_dataset('json', data_files='your_dataset.json', split='train')

def preprocess(examples):
    questions = examples['question']
    contexts = examples['context']
    inputs = tokenizer(questions, contexts, truncation=True, padding='max_length', max_length=512)
    # You need to add proper label processing for start/end positions here
    return inputs

tokenized_dataset = dataset.map(preprocess, batched=True)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    save_steps=500,
    save_total_limit=2,
    evaluation_strategy="steps",
    eval_steps=500,
    logging_steps=100,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()

# Save fine-tuned model
model.save_pretrained('./fine_tuned_model')
tokenizer.save_pretrained('./fine_tuned_model')


#The code below is to deploy in your app.py (flask app) later on
"""
from transformers import DistilBertForQuestionAnswering, DistilBertTokenizer

model = DistilBertForQuestionAnswering.from_pretrained('./fine_tuned_model')
tokenizer = DistilBertTokenizer.from_pretrained('./fine_tuned_model')

"""

#for instance, your example format could be below:
"""
{
  "context": "The Parliament of New Zealand enacts as follows:",
  "question": "Who enacts the law in New Zealand?",
  "answers": {
    "text": ["The Parliament of New Zealand"],
    "answer_start": [0]
  }
}

"""

#Then you can import to here:
"""
import json

# Load examples from your JSON file
with open('your_examples.json', 'r', encoding='utf-8') as f:
    examples = json.load(f) 
"""

#recommend to do so
"""
from datasets import Dataset

dataset = Dataset.from_list(examples)


"""

#next process and tokenize the examples for QA training 

"""
from transformers import DistilBertTokenizerFast

tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased-distilled-squad')

def prepare_features(example):
    # Tokenize question and context
    tokenized_example = tokenizer(
        example['question'],
        example['context'],
        truncation=True,
        max_length=512,
        padding='max_length',
        return_offsets_mapping=True
    )
    
    # Since answers can be multiple, take the first answer (or adjust as needed)
    answer = example['answers']['text'][0]
    answer_start_char = example['answers']['answer_start'][0]
    answer_end_char = answer_start_char + len(answer)
    
    # Find token start and end positions of the answer
    offsets = tokenized_example['offset_mapping']
    
    token_start_index = 0
    token_end_index = 0

    # Identify the tokens that correspond to the answer span
    for idx, (start, end) in enumerate(offsets):
        if start <= answer_start_char < end:
            token_start_index = idx
        if start < answer_end_char <= end:
            token_end_index = idx
            break
    
    tokenized_example['start_positions'] = token_start_index
    tokenized_example['end_positions'] = token_end_index
    
    # Remove offset mapping (not needed for training)
    tokenized_example.pop('offset_mapping')

    return tokenized_example

tokenized_dataset = dataset.map(prepare_features)
""" 

#Finally This tokenized_dataset now contains tokenized inputs along with the correct start and end token positions for answers, ready for training with Trainer