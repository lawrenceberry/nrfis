from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from .. import Package, basement_package, strong_floor_package, steel_frame_package
from ..dependencies import get_db
from ..calculations import Calculations
from ..schemas.fbg import DataType, Schemas

router = APIRouter()


class DataCollector:
    def __init__(self, package: Package):
        self.package = package

    def __call__(
        self,
        session: Session = Depends(get_db),
        data_type: DataType = Query(
            ..., alias="data-type", description="The type of data requested."
        ),
        start_time: datetime = Query(
            ...,
            alias="start-time",
            description=" ISO 8601 format string representing the start time of the range of data requested.",
            example="2020-02-01T17:28:14.723333",
        ),
        end_time: datetime = Query(
            ...,
            alias="end-time",
            description=" ISO 8601 format string representing the end time of the range of data requested.",
            example="2020-02-01T17:28:14.723333",
        ),
    ):
        if start_time > end_time:
            raise HTTPException(
                status_code=422, detail="Start time is later than end time"
            )

        raw_data = (
            session.query(self.package.values_table)
            .filter(self.package.values_table.timestamp > start_time)
            .filter(self.package.values_table.timestamp < end_time)
            .all()
        )

        if data_type == DataType.raw:
            return raw_data

        metadata = {
            row.uid: row for row in session.query(self.package.metadata_table).all()
        }

        selected_sensors = [
            uid for uid, sensor in metadata.items() if sensor.type == data_type.value
        ]

        return [
            {
                "timestamp": row.timestamp,
                **{
                    (metadata[uid].name or uid): Calculations[self.package][data_type](
                        uid, row, metadata
                    )
                    for uid in selected_sensors
                },
            }
            for row in raw_data
        ]


@router.get("/basement/", response_model=List[Schemas[basement_package]])
def get_basement_data(data=Depends(DataCollector(basement_package))):
    """
    Fetch FBG sensor data from the basement raft and perimeter walls for a particular time period.
    """
    return data


@router.get("/strong-floor/", response_model=List[Schemas[strong_floor_package]])
def get_strong_floor_data(data=Depends(DataCollector(strong_floor_package))):
    """
    Fetch FBG sensor data from the strong floor for a particular time period.
    """
    return data


@router.get("/steel-frame/", response_model=List[Schemas[steel_frame_package]])
def get_steel_frame_data(data=Depends(DataCollector(steel_frame_package))):
    """
    Fetch FBG sensor data from the steel frame for a particular time period.
    """
    return data
