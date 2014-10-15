# -*- coding: utf-8 -*-
"""
    fantasy.players.models
    ~~~~~~~~~

    player models.

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

import json

from ..extensions import db

def flatten_dict(root, prefix_keys=True):
    dicts = [([], root)]
    ret = {}
    seen = set()
    for path, d in dicts:
        if id(d) in seen:
            continue
        seen.add(id(d))
        for k, v in d.items():
            new_path = path + [k]
            prefix = '_'.join(new_path) if prefix_keys else k
            if hasattr(v, 'items'):
                dicts.append((new_path, v))
            else:
                ret[prefix] = v
    return ret

class Team(db.Document):
    name = db.StringField(unique=True)


class Player(db.Document):
    """  All the players!
    """
    name = db.StringField(unique=True)
    team = db.ReferenceField(Team)
    pos = db.StringField()
    stats = db.DictField()
    proj = db.DictField()
    zscores = db.DictField()
    drafted = db.BooleanField(default=False)
    rank = db.IntField()
    ranks = db.DictField()
    price = db.IntField()
    keep = db.BooleanField(default=False)
    owner = db.StringField()
    draft_pos = db.StringField()
    rank_big = db.IntField()

    meta = {
        'ordering': ['rank']
    }

    def clean(self):
        self.rank_big = self.set_rank_big()

    def set_rank_big(self):
        return self.ranks['RANK_BIG']

    @property
    def sorted_stats(self):
        stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.stats.items()}
        return list((i, stats.get(i)) for i in stat_order)

    @property
    def sorted_proj(self):
        stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.proj['AVG'].items()}
        return list((i, stats.get(i)) for i in stat_order)


    def flatten(self):
        """ MongoDB Object to JSON Object
            Returns flat JSON of model
        """
        data = json.loads(self.to_json())
        data.pop('_cls', None)
        for key, val in list(data.items()):
            if key == 'team':
                data[key] = str(self[key].name)
            elif key == '_id':
                data[key] = str(self.id)
        data = flatten_dict(data)
        return data
