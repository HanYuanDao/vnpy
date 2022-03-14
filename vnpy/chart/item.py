from abc import abstractmethod
from typing import List, Dict, Tuple

import pyqtgraph as pg

from vnpy.trader.ui import QtCore, QtGui, QtWidgets, Qt
from vnpy.trader.object import BarData, TickData

from .base import BLACK_COLOR, UP_COLOR, DOWN_COLOR, PEN_WIDTH, BAR_WIDTH
from .manager import BarManager


class ChartItem(pg.GraphicsObject):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__()

        self._manager: BarManager = manager

        self._bar_picutures: Dict[int, QtGui.QPicture] = {}
        self._item_picuture: QtGui.QPicture = None

        self._black_brush: QtGui.QBrush = pg.mkBrush(color=BLACK_COLOR)

        self._up_pen: QtGui.QPen = pg.mkPen(
            color=UP_COLOR, width=PEN_WIDTH
        )
        self._up_brush: QtGui.QBrush = pg.mkBrush(color=UP_COLOR)

        self._down_pen: QtGui.QPen = pg.mkPen(
            color=DOWN_COLOR, width=PEN_WIDTH
        )
        self._down_brush: QtGui.QBrush = pg.mkBrush(color=DOWN_COLOR)

        self._rect_area: Tuple[float, float] = None

        # Very important! Only redraw the visible part and improve speed a lot.
        self.setFlag(self.ItemUsesExtendedStyleOption)

    @abstractmethod
    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """
        Draw picture for specific bar.
        """
        pass

    @abstractmethod
    def boundingRect(self) -> QtCore.QRectF:
        """
        Get bounding rectangles for item.
        """
        pass

    @abstractmethod
    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        pass

    @abstractmethod
    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        pass

    def update_history(self, history: List[BarData]) -> BarData:
        """
        Update a list of bar data.
        """
        self._bar_picutures.clear()

        bars = self._manager.get_all_bars()
        for ix, bar in enumerate(bars):
            self._bar_picutures[ix] = None

        self.update()

    def update_bar(self, bar: BarData) -> BarData:
        """
        Update single bar data.
        """
        ix = self._manager.get_index(bar.datetime)

        self._bar_picutures[ix] = None

        self.update()

    def update(self) -> None:
        """
        Refresh the item.
        """
        if self.scene():
            self.scene().update()

    def paint(
        self,
        painter: QtGui.QPainter,
        opt: QtWidgets.QStyleOptionGraphicsItem,
        w: QtWidgets.QWidget
    ):
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        rect = opt.exposedRect

        min_ix = int(rect.left())
        max_ix = int(rect.right())
        max_ix = min(max_ix, len(self._bar_picutures))

        rect_area = (min_ix, max_ix)
        if rect_area != self._rect_area or not self._item_picuture:
            self._rect_area = rect_area
            self._draw_item_picture(min_ix, max_ix)

        self._item_picuture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self._item_picuture = QtGui.QPicture()
        painter = QtGui.QPainter(self._item_picuture)

        for ix in range(min_ix, max_ix):
            bar_picture = self._bar_picutures[ix]

            if bar_picture is None:
                bar = self._manager.get_bar(ix)
                bar_picture = self._draw_bar_picture(ix, bar)
                self._bar_picutures[ix] = bar_picture

            bar_picture.play(painter)

        painter.end()

    def clear_all(self) -> None:
        """
        Clear all data in the item.
        """
        self._item_picuture = None
        self._bar_picutures.clear()
        self.update()


class CandleItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """"""
        # Create objects
        candle_picture = QtGui.QPicture()
        painter = QtGui.QPainter(candle_picture)

        if isinstance(bar, TickData):
            bar.open_price = bar.ask_price_1
            bar.high_price = bar.ask_price_5
            bar.low_price = bar.bid_price_5
            bar.close_price = bar.bid_price_1

        # Set painter color
        if bar.close_price >= bar.open_price:
            painter.setPen(self._up_pen)
            painter.setBrush(self._black_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw candle shadow
        if bar.high_price > bar.low_price:
            painter.drawLine(
                QtCore.QPointF(ix, bar.high_price),
                QtCore.QPointF(ix, bar.low_price)
            )

        # Draw candle body
        if bar.open_price == bar.close_price:
            painter.drawLine(
                QtCore.QPointF(ix - BAR_WIDTH, bar.open_price),
                QtCore.QPointF(ix + BAR_WIDTH, bar.open_price),
            )
        else:
            rect = QtCore.QRectF(
                ix - BAR_WIDTH,
                bar.open_price,
                BAR_WIDTH * 2,
                bar.close_price - bar.open_price
            )
            painter.drawRect(rect)

        # Finish
        painter.end()
        return candle_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_price, max_price = self._manager.get_price_range()
        rect = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_picutures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)

        if isinstance(bar, TickData):
            bar.open_price = bar.ask_price_1
            bar.high_price = bar.ask_price_5
            bar.low_price = bar.bid_price_5
            bar.close_price = bar.bid_price_1

        if bar:
            # if isinstance(bar, TickData):
            #     words = [
            #         "Date",
            #         bar.datetime.strftime("%Y-%m-%d"),
            #         "",
            #         "Time",
            #         bar.datetime.strftime("%H:%M:%S.%f"),
            #         "",
            #         "Open",
            #         str(bar.ask_price_1),
            #         "",
            #         "High",
            #         str(bar.ask_price_5),
            #         "",
            #         "Low",
            #         str(bar.bid_price_5),
            #         "",
            #         "Close",
            #         str(bar.bid_price_1)
            #     ]
            # else:
            #     words = [
            #         "Date",
            #         bar.datetime.strftime("%Y-%m-%d"),
            #         "",
            #         "Time",
            #         bar.datetime.strftime("%H:%M"),
            #         "",
            #         "Open",
            #         str(bar.open_price),
            #         "",
            #         "High",
            #         str(bar.high_price),
            #         "",
            #         "Low",
            #         str(bar.low_price),
            #         "",
            #         "Close",
            #         str(bar.close_price)
            #     ]

            words = [
                "Date",
                bar.datetime.strftime("%Y-%m-%d"),
                "",
                "Time",
                bar.datetime.strftime("%H:%M:%S.%f"),
                "",
                "Open",
                str(bar.open_price),
                "",
                "High",
                str(bar.high_price),
                "",
                "Low",
                str(bar.low_price),
                "",
                "Close",
                str(bar.close_price)
            ]
            text = "\n".join(words)
        else:
            text = ""

        return text


class VolumeItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """"""
        # Create objects
        volume_picture = QtGui.QPicture()
        painter = QtGui.QPainter(volume_picture)

        # Set painter color
        if bar.close_price >= bar.open_price:
            painter.setPen(self._up_pen)
            painter.setBrush(self._up_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw volume body
        rect = QtCore.QRectF(
            ix - BAR_WIDTH,
            0,
            BAR_WIDTH * 2,
            bar.volume
        )
        painter.drawRect(rect)

        # Finish
        painter.end()
        return volume_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_volume, max_volume = self._manager.get_volume_range()
        rect = QtCore.QRectF(
            0,
            min_volume,
            len(self._bar_picutures),
            max_volume - min_volume
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_volume, max_volume = self._manager.get_volume_range(min_ix, max_ix)
        return min_volume, max_volume

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)

        if bar:
            text = f"Volume {bar.volume}"
        else:
            text = ""

        return text


class TickLineItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__(manager)
        # self.point_pen = pg.mkPen(color=(255, 255, 255), width=8)
        self.point_pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 1, QtCore.Qt.SolidLine)
        self.point_Brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.point_Brush.setStyle(QtCore.Qt.SolidPattern)

    def _draw_bar_picture(self, ix: int, tick: TickData) -> QtGui.QPicture:
        """"""
        # Create objects
        tick_line_picture = QtGui.QPicture()
        painter = QtGui.QPainter(tick_line_picture)

        # Set painter color
        painter.setPen(self.point_pen)
        painter.setBrush(self.point_Brush)
        # painter.setPen(self._down_pen)
        # painter.setBrush(self._down_brush)

        rect = QtCore.QRectF(
            ix - 0.1,
            tick.last_price - 0.5,
            0.1 * 2,
            1
        )
        painter.drawRect(rect)
        # painter.drawPoint(QtCore.QPointF(ix, tick.last_price))

        # Finish
        painter.end()
        return tick_line_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_price, max_price = self._manager.get_price_range()
        rect = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_picutures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        tick = self._manager.get_bar(ix)

        ask_total_volume = tick.ask_volume_1+tick.ask_volume_2+tick.ask_volume_3+tick.ask_volume_4+tick.ask_volume_5
        bid_total_volume = tick.bid_volume_1+tick.bid_volume_2+tick.bid_volume_3+tick.bid_volume_4+tick.bid_volume_5

        if tick:
            words = [
                "Date",
                tick.datetime.strftime("%Y-%m-%d"),
                "",
                "Time",
                tick.datetime.strftime("%H:%M:%S.%f")[:-3],
                "",
                "ask_price_5",
                str(tick.ask_price_5),
                "",
                "ask_price_1",
                str(tick.ask_price_1),
                "",
                "last_price",
                str(tick.last_price),
                "",
                "bid_price_1",
                str(tick.bid_price_1),
                "",
                "bid_price_5",
                str(tick.bid_price_5),
                "",
                "ask_total_volume/bid_total_volume",
                "NaN" if (bid_total_volume == 0) else str(ask_total_volume / bid_total_volume)
            ]
            text = "\n".join(words)
        else:
            text = ""

        return text


class TickVolumeItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, tick: TickData) -> QtGui.QPicture:
        """"""
        # Create objects
        volume_picture = QtGui.QPicture()
        painter = QtGui.QPainter(volume_picture)

        # Set painter color
        painter.setPen(self._down_pen)
        painter.setBrush(self._down_brush)

        # Draw volume body
        rect = QtCore.QRectF(
            ix - BAR_WIDTH,
            0,
            BAR_WIDTH * 2,
            tick.volume
        )
        painter.drawRect(rect)

        # Finish
        painter.end()
        return volume_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_volume, max_volume = self._manager.get_volume_range()
        rect = QtCore.QRectF(
            0,
            min_volume,
            len(self._bar_picutures),
            max_volume - min_volume
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_volume, max_volume = self._manager.get_volume_range(min_ix, max_ix)
        return min_volume, max_volume

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)

        if bar:
            text = f"Volume {bar.volume}"
        else:
            text = ""

        return text