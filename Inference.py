# import argparse
from fastsam import FastSAM, FastSAMPrompt 
# import ast
import torch
from PIL import Image

try:
    import open_clip
except Exception as e:
    print(f'{e}', 'we use open-clip instead please search on google about |open-clip| for more detail')
    raise

model_path = '/home/works/FastSAM-x.pt'
img_path = 'images/test1.png'
imgsz = 1024
iou = 0.9

text_prompt = 'the box, the luggage, the bag ,a person ,the road, a light,the traffic cone,the road sign, the car, the number digits, The white road line, A background'

idx_obs = [0,1,2,3]
# idx_obs = None
conf = 0.4
device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
randomcolor = True
withContours = True
retina = True


model = FastSAM(model_path)

clip_coder,_,clip_preprocess = open_clip.create_model_and_transforms('ViT-B-16', pretrained='datacomp_l_s1b_b8k')
tokenizer = open_clip.get_tokenizer('ViT-B-16')
clip_coder.to(device)

# Get image here
textPrepList = text_prompt.split(',')
text_tokens = tokenizer(textPrepList).to(device)
with torch.no_grad():
    # image_features = model.encode_image(image_input).float()
    text_features = clip_coder.encode_text(text_tokens).float()

text_features /= text_features.norm(dim=-1, keepdim=True)




input = Image.open(img_path)

input = input.convert("RGB")

# Call here

everything_results = model(
    input,
    device=device,
    retina_masks=retina,
    imgsz=imgsz,
    conf=conf,
    iou=iou    
    )
bboxes = None
points = None
point_label = None

#image, results,image_encoder,pre_texts_norm,clip_preprocess

# prompt_process = FastSAMPrompt(input, everything_results, device=device)
prompt_process = FastSAMPrompt(input,everything_results,clip_coder,text_features,clip_preprocess)
if idx_obs != None:
    ann = prompt_process.prep_texts_prompt(idx_observation = idx_obs,objstr=textPrepList)

else:
    ann = prompt_process.everything_prompt()

print(ann.shape)
# print('hihihihihihihi')

prompt_process.plot(
    annotations=ann,
    output_path='output/'+img_path.split("/")[-1],
    bboxes = bboxes,
    points = points,
    point_label = point_label,
    withContours=withContours,
    better_quality=False,
)




# if __name__ == "__main__":
#     # args = parse_args()
#     main()#args)
