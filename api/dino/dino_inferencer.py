import torch
import torch.backends.cudnn as cudnn
from dino import utils
from dino import vision_transformer as vits
from torch import nn
from torchvision import transforms as pth_transforms


class LinearClassifier(nn.Module):
    """Linear layer to train on top of frozen features"""

    def __init__(self, dim, num_labels=1000):
        super(LinearClassifier, self).__init__()
        self.num_labels = num_labels
        self.linear = nn.Linear(dim, num_labels)
        self.linear.weight.data.normal_(mean=0.0, std=0.01)
        self.linear.bias.data.zero_()

    def forward(self, x):
        # flatten
        x = x.view(x.size(0), -1)

        # linear layer
        return self.linear(x)


class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ViTInferencer:
    def __init__(
        self,
        model_path: str,
    ):
        args = DotDict()
        args.rank = 0
        args.world_size = 1
        args.gpu = 0
        utils.init_distributed_mode(args)
        cudnn.benchmark = True

        model = vits.__dict__["vit_small"](patch_size=16, num_classes=0)
        embed_dim = model.embed_dim * (4 + 0)

        linear_classifier = LinearClassifier(embed_dim, num_labels=23)
        linear_classifier = linear_classifier.cuda()
        linear_classifier = nn.parallel.DistributedDataParallel(
            linear_classifier,
            # TODO: Add device_ids=
        )

        model.cuda()
        model.eval()
        linear_classifier.eval()

        utils.load_pretrained_end_to_end_model(
            model,
            linear_classifier,
            model_path,
            "vit_small",
            16,
        )

        self.model = model
        self.linear_classifier = linear_classifier

    def __call__(self, images):
        outputs = []

        for image in images:
            image = pth_transforms.ToTensor()(image).unsqueeze(0).cuda()
            with torch.no_grad():
                intermediate_output = self.model.get_intermediate_layers(image, 4)
                output = torch.cat([x[:, 0] for x in intermediate_output], dim=-1)
            scores = self.linear_classifier(output)[0]
            scores = torch.nn.functional.softmax(scores, dim=-1)
            predicted_label = torch.argmax(scores, dim=-1).item()
            outputs.append(
                {
                    "scores": scores.tolist(),
                    "predicted_label": predicted_label,
                    "confidence": scores[predicted_label].item(),
                }
            )

        return outputs
