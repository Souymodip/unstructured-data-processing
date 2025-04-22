import os
import pandas as pd
import matplotlib.pyplot as plt
import imageio


# sample_series = [
#     [1, 2, 3, 4, 3, 2, 1, 2, 3, 4],
#     [2, 3, 4, 5, 4, 3, 2, 1, 2, 3],
#     [3, 4, 5, 6, 5, 4, 3, 2, 3, 4],
#     [4, 5, 6, 7, 6, 5, 4, 3, 2, 1],
# ]
# csv_paths = []
# for i, series in enumerate(sample_series):
#     df = pd.DataFrame(series, columns=['value'])
#     path = f'/mnt/data/test_csvs/data{i+1}.csv'
#     df.to_csv(path, index=False)
#     csv_paths.append(path)

# 2. Define plotting & GIF assembly functions
def plot_frame(values, output_path):
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#a061d6')
    ax.set_facecolor('#a061d6')
    x = range(len(values))
    y = values

    # Bars
    for xi, yi in zip(x, y):
        ax.vlines(xi, 0, yi, color='white', alpha=0.3)

    # Line + markers
    ax.plot(x, y, color='white', linewidth=2)
    ax.scatter(x, y, color='white', s=40, zorder=3)

    # Highlight peak
    peak_idx = int(pd.Series(y).idxmax())
    peak_val = y[peak_idx]
    ax.scatter(peak_idx, peak_val, facecolors='none', edgecolors='white',
               s=200, linewidth=2, zorder=4)
    ax.hlines([peak_val * 0.85, peak_val * 0.75],
              peak_idx + 1, peak_idx + 3,
              color='white', alpha=0.4, linewidth=3)

    ax.set_axis_off()
    plt.margins(0)
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


def make_animation(csv_list, out_dir, gif_path, duration=0.5):
    os.makedirs(out_dir, exist_ok=True)
    frame_files = []
    for i, csv_file in enumerate(csv_list):
        df = pd.read_csv(csv_file)
        values = df['value'].tolist()
        frame_path = os.path.join(out_dir, f'frame_{i+1}.png')
        plot_frame(values, frame_path)
        frame_files.append(frame_path)

    with imageio.get_writer(gif_path, mode='I', duration=duration) as writer:
        for fp in frame_files:
            writer.append_data(imageio.imread(fp))


def main():
    # 1. Create sample CSVs
    os.makedirs('test_csvs', exist_ok=True)
    sample_series = [
        [1, 2, 3, 4, 3, 2, 1, 2, 3, 4],
        [2, 3, 4, 5, 4, 3, 2, 1, 2, 3],
        [3, 4, 5, 6, 5, 4, 3, 2, 3, 4],
        [4, 5, 6, 7, 6, 5, 4, 3, 2, 1],
    ]
    csv_paths = []
    for i, series in enumerate(sample_series):
        df = pd.DataFrame(series, columns=['value'])
        path = f'test_csvs/data{i + 1}.csv'
        df.to_csv(path, index=False)
        csv_paths.append(path)
    # 3. Run the animation creation
    frames_dir = 'test_csvs/test_frames'
    gif_file = 'test_csvs/test_animation.gif'
    make_animation(csv_paths, frames_dir, gif_file, duration=0.6)

    # 4. Display the four generated PNG frames in a 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    for idx, ax in enumerate(axes.flatten()):
        img = imageio.imread(os.path.join(frames_dir, f'frame_{idx+1}.png'))
        ax.imshow(img)
        ax.axis('off')
    plt.show()

    print(f"Animated GIF saved to: {gif_file}")


if __name__ == "__main__":
    main()
