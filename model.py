import torch

class BinaryClassifier(torch.nn.Module):
    def __init__(self,input_dim, num_classes):
        super(BinaryClassifier, self).__init__()
        self.dropout = torch.nn.Dropout(0.1)
        self.f1 = torch.nn.Linear(input_dim, input_dim * 2)
        self.activation = torch.nn.Softsign()
        self.f2 = torch.nn.Linear( input_dim * 2, input_dim)
        self.f3 = torch.nn.Linear( input_dim, num_classes)
        self.softmax = torch.nn.Softmax()
        
        
    def forward(self,embedding, label = None):
        x = self.dropout(embedding)
        x = self.f1(x)
        x = self.activation(x)
        x = self.f2(x)
        x = self.activation(x)
        x = self.f3(x)
        loss = 0
        if label:
            label = torch.LongTensor(label).to(device)
            loss_fc = torch.nn.CrossEntropyLoss()
            loss = loss_fc(x, label)
        # todo use softmax, wenn noch labels enabled
        return (loss, x)