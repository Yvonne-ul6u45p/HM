
import  os

k = 1920 * 1080
k = k * 3
shape = (1080, 1920)
source_path = '/mnt/sdb/Datasets/TestVideo/raw_video_1080/UVG/Beauty_1920x1080_120.yuv'

# source_path = '/home/pc3502/HM17/420/HEVC-B_YUV420/qp=19/BQTerrace/BQTerrace_1920x1080_60.yuv'

# source_path = '/home/pc3502/HM/CLIC2022_YUV420/0d49152a92ce3b843968bf2e131ea5bc5e409ab056196e8c373f9bd2d31b303d.yuv'
num_frames = os.path.getsize(source_path)
print(num_frames)
print(num_frames % k)
print(k)
print(num_frames // k)
exit()
num_frames = num_frames // 255
# print(os.path.getsize(source_path) // (shape[0] * shape[1] * 3 // 2))
print(num_frames)
print(k)
print(num_frames - k -k//2)
print(num_frames - k)
print(num_frames - k//4)
print(num_frames - k//2)
# with open(dest_path, 'wb') as dest: