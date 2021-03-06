import { Component, OnInit } from '@angular/core';

import { UserService } from '../user.service';

import { UserData, RankData } from '../models/user';

@Component({
  selector: 'app-ranking',
  templateUrl: './ranking.component.html',
  styleUrls: ['./ranking.component.css']
})
export class RankingComponent implements OnInit {
  public userData: UserData = new UserData();
  public ranks: RankData[] = [];
  public timeFrame = 'all';

  constructor(private _userService: UserService) { }

  ngOnInit() {
    this.getRankings();
  }

  getRankings() {
    this._userService.getRanking(this.timeFrame).then(ranks => {
      this.ranks = ranks;
    });
  }

  onTimeFrameChange() {
    this.getRankings();
  }
}
