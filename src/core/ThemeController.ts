/**
 * ThemeController.ts - org.telegram.ui.ActionBar.Theme
 */

export interface MessageGroupingState {
  isGroupStart?: boolean;
  isGroupMiddle?: boolean;
  isGroupEnd?: boolean;
  isSingle?: boolean;
}

export class ThemeController {
  private static instance: ThemeController;

  public static getInstance(): ThemeController {
    if (!ThemeController.instance) {
      ThemeController.instance = new ThemeController();
    }
    return ThemeController.instance;
  }

  /**
   * Computes authentic Telegram message bubble corner radii based on message grouping and language direction
   */
  public getBubbleRadiusStyle(
    isOutgoing: boolean,
    grouping?: MessageGroupingState,
    isRtl: boolean = false
  ): string {
    const isSingle =
      grouping?.isSingle ??
      (!grouping?.isGroupStart && !grouping?.isGroupMiddle && !grouping?.isGroupEnd);
    const isStart = grouping?.isGroupStart;
    const isMiddle = grouping?.isGroupMiddle;
    const isEnd = grouping?.isGroupEnd;

    if (isOutgoing) {
      if (isRtl) {
        if (isSingle) return '16px 16px 16px 4px';
        if (isStart) return '16px 16px 16px 6px';
        if (isMiddle) return '6px 16px 16px 6px';
        if (isEnd) return '6px 16px 16px 4px';
        return '16px 16px 16px 4px';
      } else {
        if (isSingle) return '16px 16px 4px 16px';
        if (isStart) return '16px 16px 6px 16px';
        if (isMiddle) return '16px 6px 6px 16px';
        if (isEnd) return '16px 6px 4px 16px';
        return '16px 16px 4px 16px';
      }
    } else {
      if (isRtl) {
        if (isSingle) return '16px 16px 4px 16px';
        if (isStart) return '16px 16px 6px 16px';
        if (isMiddle) return '16px 6px 6px 16px';
        if (isEnd) return '16px 6px 4px 16px';
        return '16px 16px 4px 16px';
      } else {
        if (isSingle) return '16px 16px 16px 4px';
        if (isStart) return '16px 16px 16px 6px';
        if (isMiddle) return '6px 16px 16px 6px';
        if (isEnd) return '6px 16px 16px 4px';
        return '16px 16px 16px 4px';
      }
    }
  }
}

export const themeController = ThemeController.getInstance();
