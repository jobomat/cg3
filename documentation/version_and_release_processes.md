## new file process

+ open template file
+ search and replace
+ save modified template file

## events

+ **asset_created**
  + payload: Asset
  + listener: AssetProvider
+ **asset_version_saved**
  + payload: Asset
  + listener: AssetProvider
+ **asset_released**
  + payload: Asset
  + listener: AssetProvider
+ **asset_opened**
  + payload: Asset
  + listener: AssetProvider, AssetInformer

## version

+ prop
  + mod
    + save version file with new name
    + post event "version_saved"

## release

+ prop
  + mod
    + save version file with new name
    + copy verion file to release_history with date
    + overwrite release file with verion file
    + if no release file existed create first version file for shade

+ char
  + mod
    + save version file with new name
    + copy verion file to release_history with date
    + overwrite release file with verion file
    + if no release file existed create first version file for shade
    + if no release file existed create first version file for rig
