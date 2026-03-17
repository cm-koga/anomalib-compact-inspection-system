from omegaconf import OmegaConf
import cv2
import sys
from pathlib import Path
import pygame
from pygame.locals import *
from collections import deque
from datetime import datetime

from log import get_logger
import const
from pygame_ui import Button
from anomalib_inference import AnomalibInference, visualizer
from config import get_config
import argparse
import instance as ins

image_queue = deque(maxlen=1)
is_running = False

class ButtonUI(Button):
    def __init__(self,
                 pos,
                 size,
                 text,
                 callback,
                 args=None,
                 font_size=16,
                 bg_color=[0x19, 0x76, 0xd2],
                 bg_hover_color=[0x15, 0x65, 0xc0],
                 bg_clicked_color=[0x0d, 0x47, 0xa1],
        ):
        x = const.header_offset[0] + pos[0]
        y = const.header_offset[1] + pos[1]
        rect = [x, y, size[0], size[1]]

        super().__init__(rect, text, callback, args, font_size, bg_color, bg_hover_color, bg_clicked_color)

def finalize():
    ins.logger.info("app finalize")
    sys.exit()

def clicked_run_button(args):
    ins.logger.info("click run button")
    global is_running

    is_running = not is_running

def _save_image(save_dir, tag):
    global image_queue
    if image_queue:
        im = image_queue[-1]

        dt = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        save_path = str(save_dir / f"{dt}.png")

        cv2.imwrite(save_path, im)
        ins.logger.info(f"save {tag} image: {save_path}")


def clicked_save_image_button(args):
    global image_queue

    save_dir = args[0]
    tag = args[1]
    _save_image(save_dir, tag)

def main():
    global image_queue

    ins.logger.info("start application.")

    # initialize
    pygame.init()

    screen = pygame.display.set_mode(ins.cfg.ui.window_size)
    pygame.display.set_caption(ins.cfg.title)

    if ins.cfg.ui.bg_color is None:
        window_bg_color = [255, 255, 255]
    else:
        window_bg_color =ins.cfg.ui.bg_color

    screen.fill(window_bg_color)

    # icon
    icon = pygame.image.load(Path(__file__).parent / "resource/favicon.ico")
    pygame.display.set_icon(icon)

    # button
    button_list = []

    button_running = ButtonUI((0, 0), (80, 50), const.caption_run, callback=clicked_run_button, font_size=22)
    button_list.append(button_running)
        
    if ins.cfg.save_image.enable:
        normal_image_save_path = Path(ins.cfg.save_image.normal_image_save_path)
        abnormal_image_save_path = Path(ins.cfg.save_image.abnormal_image_save_path)
        normal_image_save_path.mkdir(parents=True, exist_ok=True)
        abnormal_image_save_path.mkdir(parents=True, exist_ok=True)

        button_list.append(
            ButtonUI((120, 0), (140, 50), "SAVE NORMAL",
                     callback=clicked_save_image_button,
                     args=[normal_image_save_path, "normal"],
                     font_size=18
                    )
        )
        button_list.append(
            ButtonUI((280, 0), (140, 50), "SAVE ABNORMAL",
                     callback=clicked_save_image_button,
                     args=[abnormal_image_save_path, "abnormal"],
                     font_size=18
                    )
        )

    # init model
    model = AnomalibInference(
        ins.cfg.model.ckpt_path,
        ins.cfg.model.cfg_path,
        cuda=ins.cfg.model.gpu
        )

    # init camera
    capture = cv2.VideoCapture(ins.cfg.camera.id)
    if not capture:
        ins.logger.error("No camera device.")
        finalize()

    # ui
    result_font = pygame.font.SysFont(None, const.result_font_size)
    score_font = pygame.font.SysFont(None, const.score_font_size)

    # main loop
    req_stop = False
    try:
        while not req_stop:
            screen.fill(window_bg_color) 

            ret, im = capture.read()
            if ret == True:
                image_queue.append(im)
                
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

                if is_running: 
                    # inference
                    pred_score, pred_label, anomaly_map, pred_mask = model.infer(im)

                    score = pred_score
                    judge = score >= ins.cfg.inspection.judge_th
                    result = "NG" if judge else "OK"
                    ins.logger.info(f"[{result}][{pred_label}] {score:.5f}")
                else:
                    judge = False
                    result = ""
                    score = 0.0

                if ins.cfg.ui.camlive_size is not None:
                    im = cv2.resize(im, ins.cfg.ui.camlive_size)

                if is_running:
                    # visualize
                    im = visualizer.overlay_heatmap(
                        im,
                        anomaly_map,
                        cut_th=ins.cfg.visualize.cut_th,
                        bgr=False,
                        normalize=ins.cfg.visualize.normalize
                        )

                # show image
                pg_img = pygame.image.frombuffer(im.tobytes(), im.shape[1::-1], "RGB")

                screen.blit(pg_img, const.camlive_offset)

            # OK/NG result
            result_rect = pygame.Rect(
                const.camlive_offset[0] + ins.cfg.ui.camlive_size[0] + 8,
                const.camlive_offset[1],
                const.result_size[0],
                const.result_size[1], 
                )
            
            if is_running:
                bg_color = (200, 50, 50) if judge else (40, 40, 170)
            else:
                bg_color = (80, 80, 80)

            pygame.draw.rect(screen, bg_color, result_rect)
            text_surf = result_font.render(result, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=result_rect.center)
            screen.blit(text_surf, text_rect)

            # score
            if is_running:
                score_text = f"{score:.5f}"
            else:
                score_text = ""
            text_surf = result_font.render(score_text, True, (40, 40, 40))
            screen.blit(
                text_surf,
                (result_rect[0], result_rect[1] + result_rect[3] + 8)
            )

            # button
            for b in button_list:
                b.draw(screen)

            #
            pygame.display.flip()

            # event
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    req_stop = True

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        req_stop = True

                for b in button_list:
                    b.handle_event(event)

    except Exception as e:
        ins.logger.exception(e)
        raise

    finally:
        finalize()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument('--cfg', default=const.config_path, help='config file path')
    args = parser.parse_args()

    ins.cfg = get_config(args.cfg)
    ins.logger = get_logger(ins.cfg.log.level)

    main()
