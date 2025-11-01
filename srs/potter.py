import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt

plt.ion()
fig = plt.figure(figsize=(4, 4))

def plot(scores, mean_scores, game_num=0, record=0):
    plt.clf()
    
    # Main title with game number and record
    plt.title(f'Training... | Game: {game_num} | Record: {record}', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    
    plt.plot(scores, label='Score', color='blue', linewidth=2)
    plt.plot(mean_scores, label='Mean Score', color='orange', linewidth=2)
    
    plt.ylim(ymin=0)
    plt.grid(True, alpha=0.3)
    
    # Display latest values
    if len(scores) > 0:
        plt.text(len(scores)-1, scores[-1], str(scores[-1]), 
                fontsize=9, color='blue')
    if len(mean_scores) > 0:
        plt.text(len(mean_scores)-1, mean_scores[-1], f'{mean_scores[-1]:.1f}', 
                fontsize=9, color='orange')
    
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    # NO PAUSE - just update the canvas
    fig.canvas.draw_idle()
    fig.canvas.flush_events()
