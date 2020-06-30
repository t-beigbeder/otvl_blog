import torch


print(torch.cuda.is_available())
print(torch.rand(2, 2))
t = torch.rand(3, 3)
print(t)
print(t.device)
t.to('cuda')
