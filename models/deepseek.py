from transformers import AutoModelForCausalLM, AutoTokenizer

class DeepseekModel():
    def __init__(self, model_name, device = 'cuda'):
        self.device = device # the device to load the model onto

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def predict(self, prompt):
        
        # CoT
        messages = [
            {"role": "user", "content": prompt},
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        pad_token_id = self.tokenizer.eos_token_id

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=2000,
            pad_token_id = pad_token_id,
            temperature=0.7
        )

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print(response)
        if "</think>\n" in response:
            return response.split("\n")[-1].strip()
        
        return None