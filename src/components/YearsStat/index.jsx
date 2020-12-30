import React from 'react';
import { INFO_MESSAGE } from 'src/utils/const';
import YearStat from 'src/components/YearStat';
import useActivities from 'src/hooks/useActivities';

const YearsStat = ({ year, onClick }) => {
  const { years } = useActivities();
  // make sure the year click on front
  let yearsArrayUpdate = years.slice();
  yearsArrayUpdate = yearsArrayUpdate.filter((x) => x !== year);
  yearsArrayUpdate.unshift(year);

  // for short solution need to refactor
  return (
    <div className="fl w-100 w-30-l pb5 pr5-l">
      <section className="pb4" style={{ paddingBottom: '0rem' }}>
        <p>
          {INFO_MESSAGE(years.length, year)}
            <br />
            <br />
            "明明这么痛苦，这么难过，为什么就是不能放弃跑步？因为全身细胞都在蠢蠢欲动，想要感受强风迎面吹拂的滋味。"
            <br />
            <p style={quoteStyle}>&ndash;&ndash;《强风吹拂》</p>
        </p>
      </section>
      <hr color="red" />
      {yearsArrayUpdate.map((year) => (
        <YearStat key={year} year={year} onClick={onClick} />
      ))}
      <YearStat key="Total" year="Total" onClick={onClick} />
    </div>
  );
};

const quoteStyle = {
    fontWeight:"bold",
    textAlign: "right"
};

export default YearsStat;
