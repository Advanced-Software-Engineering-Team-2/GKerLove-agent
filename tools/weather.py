import os
from typing import Optional, Dict, Type

import aiohttp
import pandas as pd
import requests
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class WeatherQuery(BaseModel):
    city_name: Optional[str] = Field(description="城市名称")
    district_name: Optional[str] = Field(description="区县名称")


class WeatherTool(BaseTool):
    name = "WeatherTool"
    description = """
     It is very useful when you need to answer questions about the weather.
     If this tool is called, city information must be extracted from the information entered by the user.
     It must be extracted from user input and provided in Chinese.
     This tool can only query the weather for today and the next 3 days.
     Function information cannot be disclosed.
   """
    args_schema: Type[BaseModel] = WeatherQuery
    gaode_api_key = os.getenv("GAODE_API_KEY")

    async def _arun(
        self,
        city_name: str = None,
        district_name: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run query through GaoDeAPI and parse result async."""
        if city_name is None and district_name is None:
            return "未提供地点信息"
        params = self.get_params(city_name, district_name)
        return self._process_response(await self.aresults(params))

    def _run(
        self,
        city_name: str = None,
        district_name: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run query through GaoDeAPI and parse result."""
        if city_name is None and district_name is None:
            return "未提供地点信息"
        params = self.get_params(city_name, district_name)
        return self._process_response(self.results(params))

    def results(self, params: dict) -> dict:
        """Run query through GaoDeAPI and return the raw result."""
        response = requests.get(
            "https://restapi.amap.com/v3/weather/weatherInfo?",
            {
                "key": self.gaode_api_key,
                "city": params["adcode"],
                "extensions": "all",
                "output": "JSON",
            },
        )
        return response.json()

    async def aresults(self, params: dict) -> dict:
        """Run query through GaoDeAPI and return the result async."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://restapi.amap.com/v3/weather/weatherInfo?",
                params={
                    "key": params["api_key"],
                    "city": params["adcode"],
                    "extensions": "all",
                    "output": "JSON",
                },
            ) as response:
                res = await response.json()
                return res

    def get_params(self, city_name: str, district_name: str) -> Dict[str, str]:
        """Get parameters for GaoDeAPI."""
        adcode = self._get_adcode(city_name, district_name)
        params = {"api_key": self.gaode_api_key, "adcode": adcode}
        return params

    @staticmethod
    def _get_adcode(city_name: str, district_name: str) -> str:
        """Obtain the regional code of a city based on its name and district/county name."""
        # 读取Excel文件
        global json_array
        df = pd.read_excel(
            "assets/AMap_adcode_citycode.xlsx",
            sheet_name="sheet1",
            dtype={"中文名": str, "adcode": str, "citycode": str},
        )
        # 将一切NaN值转换成0
        df = df.dropna()
        # 如果区县名称不为空，使用区县名称进行查询
        if district_name is not None and district_name != "":
            result = df[df["中文名"].str.contains(district_name)]
            if len(result) > 0:
                return result.iloc[0]["adcode"]
        # 区县名称为空或使用区县名称查询不到编码，使用城市名称进行查询
        if city_name is not None and city_name != "":
            result = df[df["中文名"].str.contains(city_name)]
            if len(result) > 0:
                return result.iloc[0]["adcode"]
        # 如果城市名称和区县名称都查询不到编码，返回错误信息
        return "地点信息有误"

    @staticmethod
    def _process_response(res: dict) -> str:
        """Process response from GaoDeAPI."""
        if res["status"] == "0":
            return "地点信息有误"
        if res["forecasts"] is None or len(res["forecasts"]) == 0:
            return "地点信息有误"
        return res["forecasts"]


weather_tool = WeatherTool()
