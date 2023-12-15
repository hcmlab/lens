from threading import Thread
from typing import Iterator


class Llama2Wrapper:
    def __init__(self, config: dict = {}):
        self.config = config
        self.model = None
        self.tokenizer = None

    def init_model(self):
        if self.model is None:
            self.model = Llama2Wrapper.create_llama2_model(
                self.config,
            )
        if not self.config.get("llama_cpp"):
            self.model.eval()

    def init_tokenizer(self):
        if self.tokenizer is None and not self.config.get("llama_cpp"):
            self.tokenizer = Llama2Wrapper.create_llama2_tokenizer(self.config)

    @classmethod
    def create_llama2_model(cls, config):
        model_name = config.get("model_name")
        load_in_8bit = config.get("load_in_8bit", True)
        import torch
        from transformers import AutoModelForCausalLM

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_8bit=load_in_8bit,
            offload_folder="offload_folder"
            )#.to(torch.device(config["device"]))
        return model

    @classmethod
    def create_llama2_tokenizer(cls, config):
        model_name = config.get("model_name")
        import torch
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return tokenizer

    def get_input_token_length(
            self, message: str, chat_history: list[tuple[str, str]], system_prompt: str
    ) -> int:
        prompt = get_prompt(message, chat_history, system_prompt)

        if self.config.get("llama_cpp"):
            input_ids = self.model.tokenize(bytes(prompt, "utf-8"))
            return len(input_ids)
        else:
            input_ids = self.tokenizer([prompt], return_tensors="np")["input_ids"]
            return input_ids.shape[-1]

    def run(
            self,
            message: str,
            chat_history: list[tuple[str, str]],
            system_prompt: str,
            max_new_tokens: int = 1024,
            temperature: float = 0.8,
            top_p: float = 0.95,
            top_k: int = 50,
    ) -> Iterator[str]:
        import torch
        prompt = get_prompt(message, chat_history, system_prompt)
        from transformers import TextIteratorStreamer

        inputs = self.tokenizer([prompt], return_tensors="pt").to(torch.device(self.config['device']))

        streamer = TextIteratorStreamer(
            self.tokenizer, timeout=10.0, skip_prompt=True, skip_special_tokens=True
        )
        generate_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            num_beams=1,
        )
        t = Thread(target=self.model.generate, kwargs=generate_kwargs)
        t.start()

        for text in streamer:
            print(text, end=' ')
            yield text



def get_prompt(
        message: str, chat_history: list[tuple[str, str]], system_prompt: str
) -> str:
    texts = [f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]
    for user_input, response in chat_history:
        texts.append(f"{user_input.strip()} [/INST] {response.strip()} </s><s>[INST] ")
    texts.append(f"{message.strip()} [/INST]")
    return "".join(texts)