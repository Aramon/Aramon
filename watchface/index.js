import { getScene, SCENE_AOD } from '@zos/app'
import {
  battery,
  cap,
  day,
  heart,
  hour,
  minute,
  second,
  space,
  statFont,
  steps,
  week,
} from './layout'

function numberWidget(box, type, unit) {
  const options = {
    x: px(box.x),
    y: px(box.y),
    w: px(box.w),
    h: px(box.h),
    font_array: statFont,
    h_space: space,
    align_h: hmUI.align.CENTER_H,
    type,
  }
  if (unit) {
    options.unit_sc = unit
    options.unit_tc = unit
    options.unit_en = unit
  }
  hmUI.createWidget(hmUI.widget.TEXT_IMG, options)
}

WatchFace({
  onInit() {},

  build() {
    const aod = getScene() === SCENE_AOD

    hmUI.createWidget(hmUI.widget.IMG, {
      x: px(0),
      y: px(0),
      w: px(480),
      h: px(480),
      src: aod ? 'images/bg_aod.png' : 'images/bg.png',
    })

    if (!aod) {
      hmUI.createWidget(hmUI.widget.IMG_WEEK, {
        x: px(week.x),
        y: px(week.y),
        week_en: week.paths,
        week_sc: week.paths,
        week_tc: week.paths,
      })

      hmUI.createWidget(hmUI.widget.IMG_DATE, {
        day_startX: px(day.x),
        day_startY: px(day.y),
        day_sc_array: day.paths,
        day_tc_array: day.paths,
        day_en_array: day.paths,
        day_align: hmUI.align.LEFT,
        day_space: day.space,
        day_zero: 1,
        day_follow: 0,
      })

      numberWidget(heart, hmUI.data_type.HEART)
      numberWidget(steps, hmUI.data_type.STEP)
      numberWidget(battery, hmUI.data_type.BATTERY, battery.unit)
    }

    hmUI.createWidget(hmUI.widget.TIME_POINTER, {
      hour_centerX: px(240),
      hour_centerY: px(240),
      hour_posX: px(hour.pivotX),
      hour_posY: px(hour.pivotY),
      hour_path: aod ? hour.aod : hour.path,
      minute_centerX: px(240),
      minute_centerY: px(240),
      minute_posX: px(minute.pivotX),
      minute_posY: px(minute.pivotY),
      minute_path: aod ? minute.aod : minute.path,
    })

    if (aod) {
      hmUI.createWidget(hmUI.widget.IMG, {
        x: px(cap.x),
        y: px(cap.y),
        src: cap.aod,
      })
      return
    }

    hmUI.createWidget(hmUI.widget.TIME_POINTER, {
      second_centerX: px(240),
      second_centerY: px(240),
      second_posX: px(second.pivotX),
      second_posY: px(second.pivotY),
      second_path: second.path,
      second_cover_path: cap.path,
      second_cover_x: px(cap.x),
      second_cover_y: px(cap.y),
    })
  },

  onDestroy() {},
})
